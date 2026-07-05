#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import csv
import json
import os
import pickle
import statistics
import time
import warnings
from pathlib import Path
from types import SimpleNamespace

from _bootstrap import setup_paths

setup_paths()


QUESTION_CSV = Path("data/question.csv")
CHUNK_DIR = Path("chunk_outputs_finals")
DOC_INDEX_DIR = Path("doc_index")
ENV_FILE = Path(".env")

CACHE_DIR = Path("cache")
QUERY_CACHE = CACHE_DIR / "cache_query_embeddings_question_csv_router.pkl"
CHUNK_EMB_CACHE = CACHE_DIR / "cache_chunk_embeddings.pkl"

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "AITeamVN/Vietnamese_Embedding_v2")
RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")


def load_pickle(path: Path, label: str, default):
    if not path.exists():
        print(f"{label} not found: {path}")
        return default
    try:
        with path.open("rb") as f:
            obj = pickle.load(f)
        print(f"Loaded {label}: {len(obj)} entries")
        return obj
    except Exception as exc:
        print(f"Could not load {label}: {exc}")
        return default


def save_outputs(results: list[dict], json_path: Path, csv_path: Path, fields: list[str]) -> None:
    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for item in results:
            writer.writerow({field: item.get(field, "") for field in fields})


def print_summary(results: list[dict], json_path: Path, csv_path: Path) -> None:
    if not results:
        print("No results.")
        return

    correct = sum(1 for item in results if item.get("is_correct") is True)
    total = len(results)
    print("\nDONE")
    print(f"Accuracy: {correct}/{total} ({correct / total * 100:.1f}%)")
    for field in ("retrieve_ms", "rerank_ms", "answer_ms", "total_from_retrieve_ms"):
        values = [float(item[field]) for item in results if item.get(field) not in ("", None)]
        if values:
            print(f"Avg {field}: {sum(values) / len(values):.1f}")
    print(f"JSON: {json_path}")
    print(f"CSV:  {csv_path}")


def timed_router_summary_retrieve(pipeline, question: str, public_ids: list[str], top_docs: int = 3):
    import numpy as np

    mdp = pipeline.multi_doc_pipeline
    retriever = mdp.retriever

    retrieve_t0 = time.perf_counter()

    query_t0 = time.perf_counter()
    query_emb = retriever.embedder.encode(question, normalize_embeddings=True)
    query_emb = np.asarray(query_emb)
    norm = np.linalg.norm(query_emb)
    if norm > 0:
        query_emb = query_emb / norm
    query_encode_ms = (time.perf_counter() - query_t0) * 1000

    doc_search_ms = 0.0
    if public_ids:
        selected_doc_ids = public_ids
        print(f"  [DocScope] direct -> {selected_doc_ids}")
    else:
        doc_t0 = time.perf_counter()
        doc_results = mdp.doc_indexer.search(question, query_emb=query_emb, top_k=top_docs)
        doc_search_ms = (time.perf_counter() - doc_t0) * 1000
        selected_doc_ids = [r["doc_id"] for r in doc_results]
        print(
            f"  [DocScope] DocIndexer -> {selected_doc_ids} "
            f"(rrf={[round(r['rrf_score'], 4) for r in doc_results]})"
        )

    doc_chunks_map = {
        doc_id: mdp.chunk_map.get(doc_id, [])
        for doc_id in selected_doc_ids
        if mdp.chunk_map.get(doc_id)
    }

    chunk_t0 = time.perf_counter()
    all_retrieved = []
    for doc_id, chunks in doc_chunks_map.items():
        retriever._cached_chunk_embs = mdp._cached_embeddings_for(chunks)
        all_retrieved.extend(
            retriever._hybrid_retrieve_from_doc(chunks, question, doc_id, query_emb)
        )
    retriever._cached_chunk_embs = None
    chunk_retrieve_ms = (time.perf_counter() - chunk_t0) * 1000

    retrieve_ms = (time.perf_counter() - retrieve_t0) * 1000

    rerank_t0 = time.perf_counter()
    if all_retrieved:
        scores = retriever.reranker.predict([(question, c["text"]) for c in all_retrieved])
        for c, score in zip(all_retrieved, scores):
            c["rerank_score"] = float(score)
    all_retrieved.sort(key=lambda x: x["rerank_score"], reverse=True)
    retrieved_chunks = all_retrieved[:retriever.final_top_k]
    rerank_ms = (time.perf_counter() - rerank_t0) * 1000

    return retrieved_chunks, selected_doc_ids, {
        "query_encode_ms": query_encode_ms,
        "doc_search_ms": doc_search_ms,
        "chunk_retrieve_ms": chunk_retrieve_ms,
        "retrieve_ms": retrieve_ms,
        "rerank_ms": rerank_ms,
    }


def run_router_summary(args: argparse.Namespace) -> int:
    from pipeline_router_summary import create_qa_pipeline
    from qa.openai_client import load_env_file
    from qa.question_io import load_router_questions
    from qa.utils import load_all_chunks

    load_env_file(ENV_FILE, override=True)

    questions = load_router_questions(QUESTION_CSV)[: args.n]
    query_cache = {}
    if args.mode == "cached":
        loaded = load_pickle(QUERY_CACHE, "query cache", {})
        query_cache = loaded if isinstance(loaded, dict) else {}

    chunks = load_all_chunks(CHUNK_DIR)
    print(f"Loaded {len(chunks)} chunks from {CHUNK_DIR}")

    pipeline = create_qa_pipeline(
        all_chunks=chunks,
        doc_index_dir=DOC_INDEX_DIR,
        embedding_model=args.embedding_model,
        rerank_model=args.rerank_model,
        router_model=args.router_model,
        answer_model=args.answer_model,
        chunk_emb_cache=CHUNK_EMB_CACHE,
    )

    output_json = Path(args.output_json or f"router_summary_latency{args.n}_{args.mode}.json")
    output_csv = Path(args.output_csv or f"router_summary_latency{args.n}_{args.mode}.csv")
    fields = [
        "question_index",
        "intent",
        "retrieve_mode",
        "ground_truth",
        "predicted",
        "is_correct",
        "query_cache_hit",
        "route_ms_excluded",
        "query_encode_ms",
        "doc_search_ms",
        "chunk_retrieve_ms",
        "retrieve_ms",
        "rerank_ms",
        "answer_ms",
        "total_from_retrieve_ms",
        "selected_docs",
        "top_chunk_ids",
    ]

    results: list[dict] = []
    for idx, q_item in enumerate(questions, start=1):
        question = q_item["question"]
        print(f"\n--- Q{idx}/{len(questions)} ---")
        print(question[:120])

        route_t0 = time.perf_counter()
        router_result = pipeline.router.route(question)
        route_ms = (time.perf_counter() - route_t0) * 1000

        measure_t0 = time.perf_counter()
        query_emb = query_cache.get(question)
        query_cache_hit = query_emb is not None

        if args.mode == "detailed":
            retrieved_chunks, selected_docs, timing = timed_router_summary_retrieve(
                pipeline, question, router_result["public_ids"]
            )
        else:
            retrieve_t0 = time.perf_counter()
            retrieved_chunks, selected_docs = pipeline.multi_doc_pipeline.retrieve_for_question(
                question=question,
                public_ids=router_result["public_ids"],
                query_emb=query_emb,
            )
            retrieve_ms = (time.perf_counter() - retrieve_t0) * 1000
            timing = {
                "query_encode_ms": "",
                "doc_search_ms": "",
                "chunk_retrieve_ms": "",
                "retrieve_ms": retrieve_ms,
                "rerank_ms": "",
            }

        context = "\n\n".join(c["text"] for c in retrieved_chunks)
        retrieve_mode = "direct" if router_result["public_ids"] else "doc_index"

        answer_t0 = time.perf_counter()
        if retrieved_chunks:
            answer_result = pipeline.answer_generator.generate_answer(
                context=context,
                question=question,
                intent=router_result["intent"],
                options=q_item.get("options"),
            )
            predicted = answer_result["answer"]
            reasoning = answer_result["reasoning"]
        else:
            predicted = "X"
            reasoning = ""
        answer_ms = (time.perf_counter() - answer_t0) * 1000
        total_from_retrieve_ms = (time.perf_counter() - measure_t0) * 1000

        truth = q_item.get("truth")
        is_correct = predicted.strip().upper() == truth.strip().upper() if truth else None
        top_chunk_ids = [c["chunk_id"] for c in retrieved_chunks]

        item = {
            "question_index": idx,
            "question": question,
            "intent": router_result["intent"],
            "public_ids": router_result["public_ids"],
            "retrieve_mode": retrieve_mode,
            "ground_truth": truth,
            "predicted": predicted,
            "is_correct": is_correct,
            "query_cache_hit": query_cache_hit if args.mode == "cached" else "",
            "route_ms_excluded": round(route_ms, 1),
            "query_encode_ms": round(timing["query_encode_ms"], 1) if timing["query_encode_ms"] != "" else "",
            "doc_search_ms": round(timing["doc_search_ms"], 1) if timing["doc_search_ms"] != "" else "",
            "chunk_retrieve_ms": round(timing["chunk_retrieve_ms"], 1) if timing["chunk_retrieve_ms"] != "" else "",
            "retrieve_ms": round(timing["retrieve_ms"], 1),
            "rerank_ms": round(timing["rerank_ms"], 1) if timing["rerank_ms"] != "" else "",
            "answer_ms": round(answer_ms, 1),
            "total_from_retrieve_ms": round(total_from_retrieve_ms, 1),
            "selected_docs": "|".join(selected_docs),
            "top_chunk_ids": "|".join(top_chunk_ids),
            "reasoning": reasoning,
        }
        results.append(item)
        save_outputs(results, output_json, output_csv, fields)

        print(
            f"intent={item['intent']} mode={retrieve_mode} pred={predicted} "
            f"truth={truth} correct={is_correct} "
            f"retrieve={item['retrieve_ms'] / 1000:.2f}s "
            f"answer={item['answer_ms'] / 1000:.2f}s "
            f"total={item['total_from_retrieve_ms'] / 1000:.2f}s"
        )

    print_summary(results, output_json, output_csv)
    return 0


def build_baseline_settings(args: argparse.Namespace) -> SimpleNamespace:
    return SimpleNamespace(
        chunk_emb_cache=CHUNK_EMB_CACHE,
        chroma_path=Path("chroma_db_viettel"),
        chroma_collection="rag",
        embedding_model=args.embedding_model,
        embedding_truncate_dim=None,
        rerank_model=args.rerank_model,
        gpt_model=args.gpt_model,
        router_model=args.router_model,
        dense_top_k=10,
        bm25_top_k=10,
        final_top_k=5,
        pub_doc_top_k=10,
    )


def run_baseline_router(args: argparse.Namespace) -> int:
    from rank_bm25 import BM25Okapi
    from sentence_transformers import CrossEncoder, SentenceTransformer

    from baseline_fusion.retrieval import (
        build_chroma_collection,
        build_context,
        hybrid_retrieve,
        load_all_chunk_texts_with_ids,
        rerank,
    )
    from qa.answer_utils import parse_answer
    from qa.openai_client import init_client, load_env_file
    from qa.question_io import load_questions
    from qa.utils import detect_public_doc_ids, tokenize_vi
    from baseline_fusion.runner import generate_answer_by_intent, route_question

    load_env_file(ENV_FILE, override=True)
    client = init_client()
    settings = build_baseline_settings(args)

    questions = load_questions(QUESTION_CSV)[: args.n]

    print(f"Loading chunks from {CHUNK_DIR}...")
    chunk_texts, chunk_ids = load_all_chunk_texts_with_ids(CHUNK_DIR)
    if not chunk_texts:
        raise RuntimeError(f"No chunks found in {CHUNK_DIR}")

    print("Building BM25...")
    bm25 = BM25Okapi([tokenize_vi(t) for t in chunk_texts])

    print(f"Loading embedder: {settings.embedding_model}")
    embedder = SentenceTransformer(settings.embedding_model)
    collection = build_chroma_collection(settings, chunk_texts, chunk_ids, embedder)

    print(f"Loading reranker: {settings.rerank_model}")
    reranker_model = CrossEncoder(settings.rerank_model)
    retrieval_state = (chunk_texts, chunk_ids, bm25, collection, embedder, reranker_model)

    output_json = Path(args.output_json or f"baseline_router_latency{args.n}.json")
    output_csv = Path(args.output_csv or f"baseline_router_latency{args.n}.csv")
    fields = [
        "question_index",
        "intent",
        "retrieve_mode",
        "ground_truth",
        "predicted",
        "is_correct",
        "format_ok",
        "route_ms_excluded",
        "query_encoded",
        "retrieve_ms",
        "rerank_ms",
        "answer_ms",
        "total_from_retrieve_ms",
        "top_chunk_ids",
    ]

    def retrieve_one(q_item: dict):
        texts, ids, bm25_obj, chroma_collection, model, ranker = retrieval_state
        question = q_item["question"]
        pub_ids = detect_public_doc_ids(question)
        query_encoded = False
        retrieve_t0 = time.perf_counter()

        if pub_ids:
            doc_chunks = [
                {"id": ids[i], "text": texts[i]}
                for i, cid in enumerate(ids)
                if any(cid.startswith(f"{doc_id}::") for doc_id in pub_ids)
            ]
            if not doc_chunks:
                query_emb = model.encode(question, normalize_embeddings=True)
                query_encoded = True
                candidates = hybrid_retrieve(
                    question,
                    query_emb,
                    bm25_obj,
                    texts,
                    ids,
                    chroma_collection,
                    settings.dense_top_k,
                    settings.bm25_top_k,
                )
                retrieve_mode = "hybrid_fallback"
            elif len(doc_chunks) <= settings.pub_doc_top_k:
                retrieve_ms = (time.perf_counter() - retrieve_t0) * 1000
                return doc_chunks, {
                    "pub_ids": pub_ids,
                    "retrieve_mode": "pub_doc_all",
                    "query_encoded": query_encoded,
                    "retrieve_ms": retrieve_ms,
                    "rerank_ms": 0.0,
                }
            else:
                candidates = doc_chunks
                retrieve_mode = "pub_doc_rerank"
        else:
            query_emb = model.encode(question, normalize_embeddings=True)
            query_encoded = True
            candidates = hybrid_retrieve(
                question,
                query_emb,
                bm25_obj,
                texts,
                ids,
                chroma_collection,
                settings.dense_top_k,
                settings.bm25_top_k,
            )
            retrieve_mode = "hybrid"

        retrieve_ms = (time.perf_counter() - retrieve_t0) * 1000
        rerank_t0 = time.perf_counter()
        top_chunks = rerank(question, candidates, ranker, settings.final_top_k)
        rerank_ms = (time.perf_counter() - rerank_t0) * 1000
        return top_chunks, {
            "pub_ids": pub_ids,
            "retrieve_mode": retrieve_mode,
            "query_encoded": query_encoded,
            "retrieve_ms": retrieve_ms,
            "rerank_ms": rerank_ms,
        }

    results: list[dict] = []
    for pos, q_item in enumerate(questions, start=1):
        question = q_item["question"]
        print(f"\n--- Q{pos}/{len(questions)} ---")
        print(question[:120])

        route_t0 = time.perf_counter()
        intent, router_public_ids, _route_s = route_question(client, q_item, settings)
        route_ms = (time.perf_counter() - route_t0) * 1000

        measure_t0 = time.perf_counter()
        top_chunks, meta = retrieve_one(q_item)
        context = build_context(top_chunks) or "Khong co ngu canh."

        answer_t0 = time.perf_counter()
        raw, answer_s, reasoning, reasoning_s = generate_answer_by_intent(
            client, q_item, context, intent, settings
        )
        answer_ms = (time.perf_counter() - answer_t0) * 1000
        total_from_retrieve_ms = (time.perf_counter() - measure_t0) * 1000

        _num, predicted, format_ok = parse_answer(raw)
        truth = q_item.get("ground_truth")
        is_correct = predicted == truth if truth else None

        item = {
            "question_index": q_item["index"] + 1,
            "question": question,
            "intent": intent,
            "router_public_ids": router_public_ids,
            "retrieve_mode": meta["retrieve_mode"],
            "ground_truth": truth,
            "predicted": predicted,
            "is_correct": is_correct,
            "format_ok": format_ok,
            "route_ms_excluded": round(route_ms, 1),
            "query_encoded": meta["query_encoded"],
            "retrieve_ms": round(meta["retrieve_ms"], 1),
            "rerank_ms": round(meta["rerank_ms"], 1),
            "answer_ms": round(answer_ms, 1),
            "total_from_retrieve_ms": round(total_from_retrieve_ms, 1),
            "top_chunk_ids": "|".join(c["id"] for c in top_chunks),
            "raw_answer": raw,
            "reasoning": reasoning,
            "reasoning_ms": round(reasoning_s * 1000, 1),
            "answer_model_ms": round(answer_s * 1000, 1),
        }
        results.append(item)
        save_outputs(results, output_json, output_csv, fields)

        print(
            f"intent={intent} mode={item['retrieve_mode']} pred={predicted} "
            f"truth={truth} correct={is_correct} "
            f"retrieve={item['retrieve_ms'] / 1000:.2f}s "
            f"rerank={item['rerank_ms'] / 1000:.2f}s "
            f"answer={item['answer_ms'] / 1000:.2f}s "
            f"total={item['total_from_retrieve_ms'] / 1000:.2f}s"
        )

    print_summary(results, output_json, output_csv)
    return 0


def collect_candidate_pairs(args: argparse.Namespace, pairs_cache: Path):
    from pipeline_router_summary import create_qa_pipeline
    from qa.openai_client import load_env_file
    from qa.question_io import load_router_questions
    from qa.utils import load_all_chunks

    load_env_file(ENV_FILE, override=True)
    questions = load_router_questions(QUESTION_CSV)[: args.n]
    query_cache = load_pickle(QUERY_CACHE, "query cache", {})
    if not isinstance(query_cache, dict):
        query_cache = {}
    chunks = load_all_chunks(CHUNK_DIR)
    print(f"Loaded {len(chunks)} chunks from {CHUNK_DIR}")

    pipeline = create_qa_pipeline(
        all_chunks=chunks,
        doc_index_dir=DOC_INDEX_DIR,
        embedding_model=args.embedding_model,
        rerank_model=args.rerank_model,
        router_model=args.router_model,
        answer_model=args.router_model,
        chunk_emb_cache=CHUNK_EMB_CACHE,
    )

    reranker = pipeline.multi_doc_pipeline.retriever.reranker
    original_predict = reranker.predict
    all_pairs: list[list[tuple[str, str]]] = []

    def capture_predict(pairs, *predict_args, **predict_kwargs):
        reranker._captured_pairs = list(pairs)
        return original_predict(pairs, *predict_args, **predict_kwargs)

    reranker.predict = capture_predict
    try:
        for idx, q_item in enumerate(questions, start=1):
            question = q_item["question"]
            print(f"  [Collect] Q{idx}/{len(questions)}: {question[:80]}")
            router_result = pipeline.router.route(question)
            query_emb = query_cache.get(question)
            reranker._captured_pairs = []
            pipeline.multi_doc_pipeline.retrieve_for_question(
                question=question,
                public_ids=router_result["public_ids"],
                query_emb=query_emb,
            )
            all_pairs.append(list(reranker._captured_pairs))
            print(f"    -> {len(reranker._captured_pairs)} candidates")
    finally:
        reranker.predict = original_predict

    with pairs_cache.open("wb") as f:
        pickle.dump(all_pairs, f)
    print(f"Candidate pairs saved -> {pairs_cache}")
    return all_pairs


def benchmark_cross_encoder(name: str, model_id: str, all_pairs: list[list[tuple[str, str]]], warmup: int) -> dict:
    from sentence_transformers import CrossEncoder

    print(f"\nLoading reranker: {name} ({model_id})")
    ce = CrossEncoder(model_id)
    print("Model loaded.")

    if all_pairs:
        sample = next((pairs for pairs in all_pairs if pairs), all_pairs[0])
        for _ in range(warmup):
            if sample:
                ce.predict(sample)
    print(f"Warm-up done ({warmup} calls).")

    latencies_ms: list[float] = []
    for idx, pairs in enumerate(all_pairs, start=1):
        if not pairs:
            continue
        t0 = time.perf_counter()
        ce.predict(pairs)
        ms = (time.perf_counter() - t0) * 1000
        latencies_ms.append(ms)
        print(f"  Q{idx}: {len(pairs)} candidates -> {ms:.1f} ms")

    if not latencies_ms:
        return {
            "model_name": name,
            "model_id": model_id,
            "n_queries": 0,
            "avg_ms": None,
            "latencies": [],
        }

    avg = statistics.mean(latencies_ms)
    med = statistics.median(latencies_ms)
    mn = min(latencies_ms)
    mx = max(latencies_ms)
    stdev = statistics.stdev(latencies_ms) if len(latencies_ms) > 1 else 0.0
    result = {
        "model_name": name,
        "model_id": model_id,
        "n_queries": len(latencies_ms),
        "avg_candidates": round(statistics.mean(len(p) for p in all_pairs if p), 1),
        "avg_ms": round(avg, 1),
        "median_ms": round(med, 1),
        "min_ms": round(mn, 1),
        "max_ms": round(mx, 1),
        "stdev_ms": round(stdev, 1),
        "latencies": [round(x, 1) for x in latencies_ms],
    }
    print(
        f"  -> avg={avg:.1f}ms median={med:.1f}ms "
        f"min={mn:.1f}ms max={mx:.1f}ms stdev={stdev:.1f}ms"
    )
    return result


def run_reranker(args: argparse.Namespace) -> int:
    warnings.filterwarnings("ignore", message=".*overflowing tokens.*")
    warnings.filterwarnings("ignore", message=".*sequence pairs.*")
    if not args.offline:
        os.environ.pop("HF_HUB_OFFLINE", None)
        os.environ.pop("TRANSFORMERS_OFFLINE", None)

    pairs_cache = Path(args.pairs_cache)
    if pairs_cache.exists() and not args.rebuild_pairs:
        all_pairs = load_pickle(pairs_cache, "candidate pairs", [])
        if not isinstance(all_pairs, list):
            all_pairs = []
    else:
        all_pairs = collect_candidate_pairs(args, pairs_cache)

    model_registry = {
        "bge": ("BGE-M3", args.rerank_model),
        "minilm": ("MiniLM-L12-base", "cross-encoder/ms-marco-MiniLM-L-12-v2"),
        "phoranker": ("PhoRanker", "itdainb/PhoRanker"),
    }

    selected = [name.strip().lower() for name in args.models.split(",") if name.strip()]
    results = []
    for key in selected:
        if key not in model_registry:
            raise ValueError(f"Unknown reranker model key: {key}")
        name, model_id = model_registry[key]
        results.append(benchmark_cross_encoder(name, model_id, all_pairs, args.warmup))

    output_json = Path(args.output_json or "reranker_latency.json")
    output_json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nFull results -> {output_json}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Unified measurement utilities.")
    sub = parser.add_subparsers(dest="command", required=True)

    rs = sub.add_parser("router-summary", help="Measure router-summary latency.")
    rs.add_argument("--n", type=int, default=20)
    rs.add_argument("--mode", choices=("simple", "cached", "detailed"), default="cached")
    rs.add_argument("--embedding-model", default=EMBEDDING_MODEL)
    rs.add_argument("--rerank-model", default=RERANK_MODEL)
    rs.add_argument("--router-model", default=GPT_MODEL)
    rs.add_argument("--answer-model", default=GPT_MODEL)
    rs.add_argument("--output-json")
    rs.add_argument("--output-csv")
    rs.set_defaults(func=run_router_summary)

    br = sub.add_parser("baseline-router", help="Measure baseline-router latency.")
    br.add_argument("--n", type=int, default=20)
    br.add_argument("--embedding-model", default=EMBEDDING_MODEL)
    br.add_argument("--rerank-model", default=RERANK_MODEL)
    br.add_argument("--router-model", default=GPT_MODEL)
    br.add_argument("--gpt-model", default=GPT_MODEL)
    br.add_argument("--output-json")
    br.add_argument("--output-csv")
    br.set_defaults(func=run_baseline_router)

    rr = sub.add_parser("reranker", help="Collect candidate pairs and benchmark rerankers.")
    rr.add_argument("--n", type=int, default=20)
    rr.add_argument("--models", default="bge,minilm,phoranker", help="Comma list: bge,minilm,phoranker")
    rr.add_argument("--embedding-model", default=EMBEDDING_MODEL)
    rr.add_argument("--rerank-model", default=RERANK_MODEL)
    rr.add_argument("--router-model", default=GPT_MODEL)
    rr.add_argument("--pairs-cache", default="candidate_pairs_cache.pkl")
    rr.add_argument("--rebuild-pairs", action="store_true")
    rr.add_argument("--offline", action="store_true")
    rr.add_argument("--warmup", type=int, default=3)
    rr.add_argument("--output-json")
    rr.set_defaults(func=run_reranker)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
