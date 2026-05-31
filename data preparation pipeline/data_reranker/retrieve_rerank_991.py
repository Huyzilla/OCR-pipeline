#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Giai đoạn 1: Retrieve top-20 + BGE-M3 rerank cho 991 câu.
Output: retrieve_rerank_991.jsonl

Mỗi entry:
{
  "index":    1,
  "question": "...",
  "intent":   "tra_cuu",
  "candidates": [
    {"chunk": "...", "chunk_id": "...", "bge_score": 0.94, "rank": 0},
    ...  (20 entries)
  ]
}

Usage:
    python retrieve_rerank_991.py \
        --question-csv  data/question.csv \
        --intent-csv    data/qwen_intent_classification.csv \
        --chunk-dir     chunk_outputs_finals/ \
        --chroma-path   chroma_db_viettel/ \
        --output        retrieve_rerank_991.jsonl \
        [--resume]
        [--top-k 20]
"""

import argparse
import csv
import json
import re
import time
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer
import chromadb

BM25_TOP_K  = 50
DENSE_TOP_K = 50
FINAL_TOP_K = 50   # giữ top-20 sau rerank


# ── Loaders ────────────────────────────────────────────────────────────────────

def load_question_csv(path: Path) -> dict[int, dict]:
    questions = {}
    with open(path, encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f), 1):
            questions[i] = {
                "question": row.get("Question", "").strip(),
                "options":  {k: row.get(k, "").strip() for k in "ABCD"},
            }
    return questions


def load_intent_csv(path: Path) -> dict[int, str]:
    intents = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            intents[int(row["question_index"])] = row["intent"].strip()
    return intents


def load_chunks(chunk_dir: Path) -> tuple[list[str], list[str]]:
    texts, ids = [], []
    for jf in sorted(chunk_dir.rglob("*.json")):
        try:
            with open(jf, encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                continue
            doc_scope = jf.parent.name
            for i, item in enumerate(data):
                text = str(item.get("page_content", "")).strip()
                if not text:
                    continue
                chunk_id = item.get("metadata", {}).get("chunk_id", f"chunk::{i}")
                texts.append(text)
                ids.append(f"{doc_scope}::{chunk_id}")
        except Exception:
            pass
    print(f"  Loaded {len(texts):,} chunks")
    return texts, ids


def tokenize_vi(text: str) -> list[str]:
    clean = re.sub(r"[^\w\s]", " ", text.lower())
    return [t for t in clean.split() if len(t) > 1]


# ── Retrieve + Rerank ──────────────────────────────────────────────────────────

def hybrid_retrieve(
    query:       str,
    query_emb:   np.ndarray,
    bm25:        BM25Okapi,
    chunk_texts: list[str],
    chunk_ids:   list[str],
    collection,
    top_k:       int = FINAL_TOP_K,
) -> list[dict]:
    """BM25 + Dense → RRF → top_k candidates."""
    bm25_scores  = bm25.get_scores(tokenize_vi(query))
    bm25_top_idx = np.argsort(bm25_scores)[-BM25_TOP_K:][::-1].tolist()

    chroma_results = collection.query(
        query_embeddings=[query_emb.tolist()],
        n_results=DENSE_TOP_K,
        include=["documents"],
    )
    text_to_idx   = {t: i for i, t in enumerate(chunk_texts)}
    dense_top_idx = [text_to_idx[d] for d in chroma_results["documents"][0]
                     if d in text_to_idx]

    k_rrf, rrf = 60, {}
    for rank, idx in enumerate(bm25_top_idx):
        rrf[idx] = rrf.get(idx, 0.0) + 1.0 / (k_rrf + rank + 1)
    for rank, idx in enumerate(dense_top_idx):
        rrf[idx] = rrf.get(idx, 0.0) + 1.0 / (k_rrf + rank + 1)

    sorted_idx = sorted(rrf, key=lambda x: rrf[x], reverse=True)[:top_k * 2]

    return [
        {
            "chunk_id":  chunk_ids[i],
            "chunk":     chunk_texts[i],
            "rrf_score": rrf[i],
        }
        for i in sorted_idx
    ]


def bge_rerank(
    query:      str,
    candidates: list[dict],
    reranker:   CrossEncoder,
    top_k:      int = FINAL_TOP_K,
) -> list[dict]:
    """BGE rerank candidates → giữ top_k, lưu score."""
    if not candidates:
        return []

    pairs  = [(query, c["chunk"]) for c in candidates]
    scores = reranker.predict(pairs)

    for c, s in zip(candidates, scores):
        c["bge_score"] = float(s)

    ranked = sorted(candidates, key=lambda x: x["bge_score"], reverse=True)

    for i, c in enumerate(ranked):
        c["rank"] = i

    return ranked[:top_k]


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question-csv",    type=Path, required=True)
    parser.add_argument("--intent-csv",      type=Path, required=True)
    parser.add_argument("--chunk-dir",       type=Path, required=True)
    parser.add_argument("--chroma-path",     type=str,  required=True)
    parser.add_argument("--output",          type=Path,
                        default=Path("retrieve_rerank_991.jsonl"))
    parser.add_argument("--embedding-model", type=str,
                        default="AITeamVN/Vietnamese_Embedding_v2")
    parser.add_argument("--rerank-model",    type=str,
                        default="BAAI/bge-reranker-v2-m3")
    parser.add_argument("--top-k",           type=int,  default=20)
    parser.add_argument("--skip-rerank",     action="store_true",
                        help="Chi retrieve hybrid BM25+dense, khong chay BGE reranker")
    parser.add_argument("--resume",          action="store_true")
    args = parser.parse_args()

    # Resume
    done_ids: set[int] = set()
    if args.resume and args.output.exists():
        with open(args.output, encoding="utf-8") as f:
            for line in f:
                done_ids.add(json.loads(line)["index"])
        print(f"Resume: {len(done_ids)} done")

    # Load data
    print("Loading questions + intents...")
    questions = load_question_csv(args.question_csv)
    intents   = load_intent_csv(args.intent_csv)
    all_indices = sorted(questions.keys())
    print(f"  {len(all_indices)} questions, {len(intents)} intents")

    # Load corpus
    print(f"\nLoading chunks from {args.chunk_dir}...")
    chunk_texts, chunk_ids = load_chunks(args.chunk_dir)

    print("Building BM25...")
    bm25 = BM25Okapi([tokenize_vi(t) for t in chunk_texts])

    print(f"Loading embedder: {args.embedding_model}")
    embedder = SentenceTransformer(args.embedding_model)

    print(f"Loading ChromaDB: {args.chroma_path}")
    chroma_client = chromadb.PersistentClient(path=args.chroma_path)
    collection    = chroma_client.get_or_create_collection(
        name="rag", metadata={"hnsw:space": "cosine"}
    )
    print(f"  ChromaDB: {collection.count():,} vectors")

    reranker = None
    if args.skip_rerank:
        print("Skipping BGE reranker (--skip-rerank)")
    else:
        print(f"Loading BGE reranker: {args.rerank_model}")
        reranker = CrossEncoder(args.rerank_model)

    # Run
    out_f     = open(args.output, "a", encoding="utf-8")
    n_total   = len(all_indices)
    n_done    = len(done_ids)
    t_start   = time.time()

    for i, idx in enumerate(all_indices, 1):
        if idx in done_ids:
            continue

        q_data   = questions.get(idx, {})
        question = q_data.get("question", "")
        intent   = intents.get(idx, "tra_cuu")

        if not question:
            continue

        # Retrieve
        query_emb  = embedder.encode(question, normalize_embeddings=True)
        candidates = hybrid_retrieve(
            question, query_emb, bm25, chunk_texts, chunk_ids,
            collection, top_k=args.top_k,
        )

        if args.skip_rerank:
            ranked = candidates[:args.top_k]
            for rank, c in enumerate(ranked):
                c["rank"] = rank
        else:
            ranked = bge_rerank(question, candidates, reranker, top_k=args.top_k)

        out_candidates = []
        for c in ranked:
            item = {
                "rank":      c["rank"],
                "chunk_id":  c["chunk_id"],
                "chunk":     c["chunk"],
                "rrf_score": round(c["rrf_score"], 6),
            }
            if "bge_score" in c:
                item["bge_score"] = c["bge_score"]
            out_candidates.append(item)

        entry = {
            "index":      idx,
            "question":   question,
            "intent":     intent,
            "options":    q_data.get("options", {}),
            "candidates": out_candidates,
        }

        out_f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        out_f.flush()
        n_done += 1

        # Progress
        elapsed = time.time() - t_start
        per_q   = elapsed / (i - len(done_ids))
        remain  = (n_total - n_done) * per_q
        top_score = 0.0
        top_score_name = "score"
        if ranked:
            if "bge_score" in ranked[0]:
                top_score = ranked[0]["bge_score"]
                top_score_name = "bge"
            else:
                top_score = ranked[0].get("rrf_score", 0.0)
                top_score_name = "rrf"

        print(f"  [{n_done:>4}/{n_total}] Q{idx:>4} "
              f"[{intent:<10}] "
              f"{len(ranked)} candidates "
              f"top_{top_score_name}={top_score:.3f} "
              f"ETA={remain/60:.1f}min")

    out_f.close()

    # Stats
    print(f"\n{'='*55}")
    print(f"DONE: {args.output}")
    with open(args.output, encoding="utf-8") as f:
        entries = [json.loads(l) for l in f if l.strip()]
    print(f"  Total entries: {len(entries):,}")
    avg_cands = sum(len(e["candidates"]) for e in entries) / len(entries)
    print(f"  Avg candidates/query: {avg_cands:.1f}")
    by_intent = {}
    for e in entries:
        by_intent[e["intent"]] = by_intent.get(e["intent"], 0) + 1
    print(f"  By intent: {by_intent}")


if __name__ == "__main__":
    main()
