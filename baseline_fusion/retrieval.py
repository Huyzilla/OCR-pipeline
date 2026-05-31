from __future__ import annotations

import pickle
import time
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable=None, **_kwargs):
        return iterable if iterable is not None else []

from baseline_fusion.prompts import create_answer_prompt
from qa.utils import detect_public_doc_ids, load_all_chunks, tokenize_vi


def load_all_chunk_texts_with_ids(chunk_dir: Path) -> tuple[list[str], list[str]]:
    records = load_all_chunks(chunk_dir)
    texts = [record.text for record in records]
    ids = [record.chunk_id for record in records]
    print(f"Loaded {len(texts)} chunks from {chunk_dir}")
    return texts, ids


def load_or_build_query_cache(questions: list[dict], embedder, cache_path: Path) -> dict[int, object]:
    cache = {}
    if cache_path.exists():
        with cache_path.open("rb") as f:
            loaded = pickle.load(f)
        if isinstance(loaded, dict):
            cache = {k: v for k, v in loaded.items() if isinstance(k, str)}
        print(f"Loaded query cache: {len(cache)} question-text entries")

    missing = [q for q in questions if q["question"] not in cache]
    if missing:
        print(f"Encoding {len(missing)} missing queries...")
        texts = [q["question"] for q in missing]
        embeddings = embedder.encode(
            texts,
            batch_size=64,
            show_progress_bar=True,
            normalize_embeddings=True,
        )
        for q, emb in zip(missing, embeddings):
            cache[q["question"]] = emb
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with cache_path.open("wb") as f:
            pickle.dump(cache, f)
        print(f"Saved query cache: {cache_path}")

    return {q["index"]: cache[q["question"]] for q in questions}


def build_chroma_collection(args, chunk_texts: list[str], chunk_ids: list[str], embedder):
    import chromadb
    import numpy as np

    print(f"Loading ChromaDB: {args.chroma_path}")
    chroma_client = chromadb.PersistentClient(path=str(args.chroma_path))
    collection = chroma_client.get_or_create_collection(
        name=args.chroma_collection,
        metadata={"hnsw:space": "cosine"},
    )
    print(f"  ChromaDB vectors: {collection.count():,}")

    if collection.count() >= len(chunk_texts):
        return collection

    print("  ChromaDB is incomplete, building/upserting chunk embeddings...")
    chunk_embs = None
    if args.chunk_emb_cache.exists():
        with args.chunk_emb_cache.open("rb") as f:
            cached = pickle.load(f)
        if isinstance(cached, np.ndarray) and cached.shape[0] == len(chunk_texts):
            chunk_embs = cached
            print(f"  Loaded chunk embedding cache: {args.chunk_emb_cache}")

    if chunk_embs is None:
        chunk_embs = embedder.encode(
            chunk_texts,
            batch_size=64,
            show_progress_bar=True,
            normalize_embeddings=True,
        )
        args.chunk_emb_cache.parent.mkdir(parents=True, exist_ok=True)
        with args.chunk_emb_cache.open("wb") as f:
            pickle.dump(chunk_embs, f)
        print(f"  Saved chunk embedding cache: {args.chunk_emb_cache}")

    for i in tqdm(range(0, len(chunk_texts), 256), desc="ChromaDB upsert"):
        collection.upsert(
            ids=chunk_ids[i : i + 256],
            embeddings=chunk_embs[i : i + 256].tolist(),
            documents=chunk_texts[i : i + 256],
        )

    print(f"  ChromaDB vectors after upsert: {collection.count():,}")
    return collection


def hybrid_retrieve(
    query: str,
    query_emb,
    bm25,
    chunk_texts: list[str],
    chunk_ids: list[str],
    collection,
    dense_top_k: int,
    bm25_top_k: int,
) -> list[dict]:
    import numpy as np

    bm25_scores = bm25.get_scores(tokenize_vi(query))
    bm25_top_idx = np.argsort(bm25_scores)[-bm25_top_k:][::-1].tolist()

    chroma_results = collection.query(
        query_embeddings=[query_emb.tolist()],
        n_results=dense_top_k,
        include=["documents", "metadatas", "distances"],
    )
    chroma_docs = chroma_results["documents"][0]
    text_to_idx = {txt: i for i, txt in enumerate(chunk_texts)}
    dense_top_idx = [text_to_idx[d] for d in chroma_docs if d in text_to_idx]

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
            "score": rrf_score[idx],
            "bm25_rank": bm25_rank.get(idx),
            "dense_rank": dense_rank.get(idx),
        }
        for idx in sorted(rrf_score, key=lambda x: rrf_score[x], reverse=True)
    ]


def rerank(query: str, candidates: list[dict], reranker, top_k: int) -> list[dict]:
    if not candidates:
        return []
    scores = reranker.predict([(query, c["text"]) for c in candidates])
    for c, score in zip(candidates, scores):
        c["rerank_score"] = float(score)
    candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
    return candidates[:top_k]


def build_context(chunks: list[dict]) -> str:
    return "\n\n---\n\n".join(c["text"] for c in chunks if c.get("text"))


def prepare_retrieval(args, questions: list[dict]):
    from rank_bm25 import BM25Okapi
    from sentence_transformers import CrossEncoder, SentenceTransformer
    import torch

    print(f"\nLoading chunks from {args.chunk_dir}...")
    chunk_texts, chunk_ids = load_all_chunk_texts_with_ids(args.chunk_dir)
    if not chunk_texts:
        raise RuntimeError(f"No chunks found in {args.chunk_dir}")

    print("Building BM25...")
    bm25 = BM25Okapi([tokenize_vi(t) for t in tqdm(chunk_texts, desc="BM25")])

    print(f"Loading embedder: {args.embedding_model}")
    embedder = SentenceTransformer(args.embedding_model)
    query_cache = load_or_build_query_cache(questions, embedder, args.query_cache)

    collection = build_chroma_collection(args, chunk_texts, chunk_ids, embedder)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading reranker: {args.rerank_model} ({device})")
    reranker = CrossEncoder(args.rerank_model, device=device)

    return chunk_texts, chunk_ids, bm25, query_cache, collection, reranker


def retrieve_one(q_item: dict, retrieval_state, args) -> tuple[list[dict], dict]:
    chunk_texts, chunk_ids, bm25, query_cache, collection, reranker = retrieval_state
    question = q_item["question"]
    q_idx = q_item["index"]
    pub_ids = detect_public_doc_ids(question)

    if pub_ids:
        t0 = time.perf_counter()
        doc_chunks = [
            {"id": chunk_ids[i], "text": chunk_texts[i]}
            for i, cid in enumerate(chunk_ids)
            if any(cid.startswith(f"{doc_id}::") for doc_id in pub_ids)
        ]
        retrieve_s = time.perf_counter() - t0

        if not doc_chunks:
            t0 = time.perf_counter()
            candidates = hybrid_retrieve(
                question, query_cache[q_idx], bm25, chunk_texts, chunk_ids,
                collection, args.dense_top_k, args.bm25_top_k,
            )
            retrieve_s = time.perf_counter() - t0

            t0 = time.perf_counter()
            top_chunks = rerank(question, candidates, reranker, args.final_top_k)
            rerank_s = time.perf_counter() - t0
            retrieve_mode = "hybrid_fallback"
        elif len(doc_chunks) <= args.pub_doc_top_k:
            top_chunks = doc_chunks
            rerank_s = 0.0
            retrieve_mode = "pub_doc_all"
        else:
            t0 = time.perf_counter()
            top_chunks = rerank(question, doc_chunks, reranker, args.pub_doc_top_k)
            rerank_s = time.perf_counter() - t0
            retrieve_mode = "pub_doc_rerank"
    else:
        t0 = time.perf_counter()
        candidates = hybrid_retrieve(
            question, query_cache[q_idx], bm25, chunk_texts, chunk_ids,
            collection, args.dense_top_k, args.bm25_top_k,
        )
        retrieve_s = time.perf_counter() - t0

        t0 = time.perf_counter()
        top_chunks = rerank(question, candidates, reranker, args.final_top_k)
        rerank_s = time.perf_counter() - t0
        retrieve_mode = "hybrid"

    return top_chunks, {
        "pub_ids": pub_ids,
        "retrieve_mode": retrieve_mode,
        "retrieve_s": retrieve_s,
        "rerank_s": rerank_s,
    }


def build_prepared_entry(q_item: dict, top_chunks: list[dict], meta: dict) -> dict:
    context = build_context(top_chunks) or "Không có ngữ cảnh."
    return {
        "q_item": q_item,
        "top_chunks": top_chunks,
        "context": context,
        "prompt": create_answer_prompt(q_item["question"], context, q_item["options"]),
        **meta,
    }


def load_prepared_cache(cache_path: Path, expected_indices: list[int]) -> list[dict] | None:
    if not cache_path.exists():
        return None
    try:
        with cache_path.open("rb") as f:
            cached = pickle.load(f)
        if not isinstance(cached, list):
            return None
        cached_indices = [item["q_item"]["index"] for item in cached]
        if cached_indices == expected_indices:
            print(f"  Full Phase 1 cache: {len(cached)} items")
            return cached
        if expected_indices[:len(cached_indices)] == cached_indices:
            print(f"  Partial Phase 1 cache: {len(cached)}/{len(expected_indices)} items")
            return cached
        print("  Phase 1 cache mismatch, rebuilding")
    except Exception as exc:
        print(f"  Phase 1 cache load failed: {exc}")
    return None


def save_prepared_cache(cache_path: Path, prepared: list[dict]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("wb") as f:
        pickle.dump(prepared, f)
    print(f"  Saved Phase 1 cache: {len(prepared)} items -> {cache_path}")


def run_phase1(
    questions_to_run: list[dict],
    all_questions: list[dict],
    args,
    existing=None,
    checkpoint_every: int = 1,
) -> list[dict]:
    existing = existing or []
    retrieval_state = prepare_retrieval(args, all_questions)
    new_prepared = []

    print(f"\nPhase 1: retrieve + rerank {len(questions_to_run)} questions")
    for q_item in tqdm(questions_to_run, desc="Retrieve+Rerank"):
        top_chunks, meta = retrieve_one(q_item, retrieval_state, args)
        new_prepared.append(build_prepared_entry(q_item, top_chunks, meta))

        if len(new_prepared) % checkpoint_every == 0:
            save_prepared_cache(args.prepared_cache, existing + new_prepared)

    save_prepared_cache(args.prepared_cache, existing + new_prepared)
    return new_prepared
