from __future__ import annotations

import json
import pickle
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from qa.question_io import load_questions
from qa.utils import load_all_chunks, tokenize_vi
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder


TARGET_INDICES = {178, 188, 203, 254, 341, 343}


def build_args() -> SimpleNamespace:
    return SimpleNamespace(
        query_cache=ROOT / "cache" / "cache_query_embeddings_question_json_embed_gist_mnr_512d.pkl",
        chunk_emb_cache=ROOT / "cache" / "cache_chunk_embeddings_embed_gist_mnr_512d_chunks1.pkl",
        chunk_dir=ROOT / "chunk_outputs1_finals",
        chroma_path=ROOT / "chroma_db_viettel_embed_gist_mnr_512d_chunks1",
        chroma_collection="rag",
        embedding_model=str(ROOT / "models" / "embed_gist_mnr"),
        embedding_truncate_dim=512,
        rerank_model=str(ROOT / "models" / "MiniLM_H384_pruned_ft"),
        dense_top_k=10,
        bm25_top_k=10,
        final_top_k=5,
        pub_doc_top_k=10,
    )


def load_retrieval_state(args: SimpleNamespace, questions: list[dict]):
    records = load_all_chunks(args.chunk_dir)
    chunk_texts = [record.text for record in records]
    chunk_ids = [record.chunk_id for record in records]
    bm25 = BM25Okapi([tokenize_vi(text) for text in chunk_texts])

    with args.chunk_emb_cache.open("rb") as f:
        chunk_embs = pickle.load(f)
    chunk_embs = np.asarray(chunk_embs)
    if chunk_embs.shape[0] != len(chunk_ids):
        raise RuntimeError(f"Chunk embedding count mismatch: {chunk_embs.shape[0]} vs {len(chunk_ids)}")

    with args.query_cache.open("rb") as f:
        raw_query_cache = pickle.load(f)
    query_cache = {}
    for q in questions:
        emb = raw_query_cache.get(q["question"])
        if emb is None:
            raise RuntimeError(f"Missing query embedding for question_index={q['index'] + 1}")
        query_cache[q["index"]] = np.asarray(emb)

    reranker = CrossEncoder(args.rerank_model)
    return chunk_texts, chunk_ids, chunk_embs, bm25, query_cache, reranker


def hybrid_retrieve_from_cache(
    query: str,
    query_emb,
    chunk_embs,
    bm25,
    chunk_texts: list[str],
    chunk_ids: list[str],
    dense_top_k: int,
    bm25_top_k: int,
) -> list[dict]:
    bm25_scores = bm25.get_scores(tokenize_vi(query))
    bm25_top_idx = np.argsort(bm25_scores)[-bm25_top_k:][::-1].tolist()

    dense_scores = chunk_embs @ query_emb
    dense_top_idx = np.argsort(dense_scores)[-dense_top_k:][::-1].tolist()

    rrf_score, bm25_rank, dense_rank = {}, {}, {}
    k_rrf = 60
    for rank, idx in enumerate(bm25_top_idx):
        rrf_score[idx] = rrf_score.get(idx, 0.0) + 1.0 / (k_rrf + rank + 1)
        bm25_rank[idx] = rank + 1
    for rank, idx in enumerate(dense_top_idx):
        rrf_score[idx] = rrf_score.get(idx, 0.0) + 1.0 / (k_rrf + rank + 1)
        dense_rank[idx] = rank + 1

    return [
        {
            "id": chunk_ids[idx],
            "text": chunk_texts[idx],
            "score": float(rrf_score[idx]),
            "bm25_rank": bm25_rank.get(idx),
            "dense_rank": dense_rank.get(idx),
        }
        for idx in sorted(rrf_score, key=lambda x: rrf_score[x], reverse=True)
    ]


def rerank_all(query: str, candidates: list[dict], reranker) -> list[dict]:
    if not candidates:
        return []
    scores = reranker.predict([(query, c["text"]) for c in candidates])
    for c, score in zip(candidates, scores):
        c["rerank_score"] = float(score)
    candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
    return candidates


def rank_of_any(ids: list[str], gold_ids: set[str]) -> int | None:
    for idx, chunk_id in enumerate(ids, start=1):
        if chunk_id in gold_ids:
            return idx
    return None


def main() -> int:
    args = build_args()
    questions = load_questions(ROOT / "data" / "question.json")
    target_questions = [q for q in questions if q["index"] + 1 in TARGET_INDICES]
    by_index = {q["index"] + 1: q for q in target_questions}
    missing = sorted(TARGET_INDICES - set(by_index))
    if missing:
        raise RuntimeError(f"Missing questions: {missing}")

    retrieval_state = load_retrieval_state(args, questions)
    chunk_texts, chunk_ids, chunk_embs, bm25, query_cache, reranker = retrieval_state

    results = []
    for q_index in sorted(TARGET_INDICES):
        q_item = by_index[q_index]
        question = q_item["question"]
        gold_ids = set(q_item.get("gold_chunk_ids") or [])

        t0 = time.perf_counter()
        candidates = hybrid_retrieve_from_cache(
            question,
            query_cache[q_item["index"]],
            chunk_embs,
            bm25,
            chunk_texts,
            chunk_ids,
            args.dense_top_k,
            args.bm25_top_k,
        )
        retrieve_s = time.perf_counter() - t0

        pre_ids = [c["id"] for c in candidates]
        pre_rank = rank_of_any(pre_ids, gold_ids)

        t0 = time.perf_counter()
        ranked = rerank_all(question, candidates, reranker)
        rerank_s = time.perf_counter() - t0

        post_ids = [c["id"] for c in ranked]
        post_rank = rank_of_any(post_ids, gold_ids)
        top5_ids = post_ids[: args.final_top_k]

        if pre_rank is None:
            layer = "embedding/retrieval: gold ngoai candidate pool"
        elif post_rank is None:
            layer = "unexpected: gold co truoc rerank nhung mat sau rerank"
        elif post_rank > args.final_top_k:
            layer = "rerank: gold co trong pool nhung bi day khoi top-5"
        else:
            layer = "not a top-5 miss"

        results.append(
            {
                "question_index": q_index,
                "question": question,
                "gold_chunk_ids": sorted(gold_ids),
                "candidate_count": len(pre_ids),
                "gold_rank_pre_rerank": pre_rank,
                "gold_rank_after_rerank": post_rank,
                "layer": layer,
                "retrieve_ms": round(retrieve_s * 1000, 1),
                "rerank_ms": round(rerank_s * 1000, 1),
                "pre_top20_ids": pre_ids,
                "post_top20_ids": post_ids,
                "top5_ids": top5_ids,
            }
        )

    out_path = ROOT / "test" / "trace_v2_gold_miss_6.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    for item in results:
        print(
            "Q{question_index}: pre={pre} post={post} n={n} layer={layer}".format(
                question_index=item["question_index"],
                pre=item["gold_rank_pre_rerank"],
                post=item["gold_rank_after_rerank"],
                n=item["candidate_count"],
                layer=item["layer"].encode("ascii", errors="ignore").decode("ascii"),
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
