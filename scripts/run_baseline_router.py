#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import time
from pathlib import Path
from types import SimpleNamespace

from _bootstrap import setup_paths

setup_paths()

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable=None, **_kwargs):
        return iterable if iterable is not None else []

from baseline_fusion.outputs import build_debug_entry, open_output_csv, write_output_row
from baseline_fusion.runner import (
    build_pipeline_items,
    generate_answer_by_intent,
    load_resume_state,
    prepare_item,
    print_dry_run,
    route_question,
)
from qa.answer_utils import parse_answer
from qa.openai_client import init_client, load_env_file
from qa.output_io import save_json_list
from qa.question_io import load_questions


DATA_DIR = Path("data")
CACHE_DIR = Path("cache")

MAX_QUESTIONS = 200
RESUME = True
DRY_RUN = False
LOAD_ENV_FILE = True
ENV_FILE = Path(".env")

QUESTION_FILE = DATA_DIR / "question.csv"
CHUNK_DIR = Path("chunk_outputs_finals")

OUTPUT_CSV = Path("baseline_router.csv")
OUTPUT_JSON = Path("baseline_router_debug.json")

QUERY_CACHE = CACHE_DIR / "cache_query_embeddings_question_csv_router.pkl"
PREPARED_CACHE = CACHE_DIR / "cache_prepared_question_csv_router.pkl"
CHUNK_EMB_CACHE = CACHE_DIR / "cache_chunk_embeddings.pkl"
CHROMA_PATH = Path("chroma_db_viettel")
CHROMA_COLLECTION = "rag"

EMBEDDING_MODEL = "AITeamVN/Vietnamese_Embedding_v2"
RERANK_MODEL = "BAAI/bge-reranker-v2-m3"
GPT_MODEL = "gpt-4o-mini"
ROUTER_MODEL = "gpt-4o-mini"

DENSE_TOP_K = 10
BM25_TOP_K = 10
FINAL_TOP_K = 5
PUB_DOC_TOP_K = 10


def run_generation_loop(args, client, pipeline_items, retrieval_state, baseline_log) -> int:
    out_f, writer = open_output_csv(args.output_csv, args.resume)
    questions_run = 0

    try:
        for item in tqdm(pipeline_items, desc="Baseline Router"):
            q_seed = item["q_item"] if args.use_prepared_cache else item
            intent, router_public_ids, route_s = route_question(client, q_seed, args)

            prep = prepare_item(item, retrieval_state, args)
            q_item = prep["q_item"]
            prep["intent"] = intent
            prep["route_s"] = route_s
            prep["router_public_ids"] = router_public_ids

            t0 = time.perf_counter()
            raw, answer_s, reasoning, reasoning_s = generate_answer_by_intent(
                client, q_item, prep["context"], intent, args
            )
            num, predicted, format_ok = parse_answer(raw)
            generation_s = time.perf_counter() - t0

            write_output_row(
                writer,
                prep,
                raw,
                predicted,
                format_ok,
                answer_s,
                generation_s,
                intent=intent,
                route_s=route_s,
                reasoning_s=reasoning_s,
            )
            out_f.flush()

            baseline_log.append(
                build_debug_entry(
                    "Baseline Router",
                    prep,
                    raw,
                    num,
                    predicted,
                    format_ok,
                    answer_s,
                    generation_s,
                    intent=intent,
                    route_s=route_s,
                    reasoning=reasoning,
                    reasoning_s=reasoning_s,
                )
            )
            save_json_list(args.output_json, baseline_log)

            questions_run += 1
            tqdm.write(f"Q{q_item['index'] + 1}: intent={intent} baseline={predicted}")
    finally:
        out_f.close()

    return questions_run


def build_settings():
    return SimpleNamespace(
        question_csv=QUESTION_FILE,
        output_csv=OUTPUT_CSV,
        output_json=OUTPUT_JSON,
        fusion_csv=Path("unused_baseline_router_fusion.csv"),
        fusion_json=Path("unused_baseline_router_fusion_debug.json"),
        query_cache=QUERY_CACHE,
        prepared_cache=PREPARED_CACHE,
        use_prepared_cache=False,
        chunk_emb_cache=CHUNK_EMB_CACHE,
        chunk_dir=CHUNK_DIR,
        chroma_path=CHROMA_PATH,
        chroma_collection=CHROMA_COLLECTION,
        embedding_model=EMBEDDING_MODEL,
        embedding_truncate_dim=None,
        rerank_model=RERANK_MODEL,
        gpt_model=GPT_MODEL,
        router_model=ROUTER_MODEL,
        dense_top_k=DENSE_TOP_K,
        bm25_top_k=BM25_TOP_K,
        final_top_k=FINAL_TOP_K,
        pub_doc_top_k=PUB_DOC_TOP_K,
        n=MAX_QUESTIONS,
        resume=RESUME,
        fusion=False,
        env_file=ENV_FILE,
        load_env_file=LOAD_ENV_FILE,
        dry_run=DRY_RUN,
    )


def main() -> int:
    args = build_settings()

    if args.dry_run:
        print_dry_run(args)
        return 0

    if not args.question_csv.exists():
        print(f"Error: question file not found: {args.question_csv}")
        return 1
    if not args.chunk_dir.exists():
        print(f"Error: chunk directory not found: {args.chunk_dir}")
        return 1

    if args.load_env_file:
        load_env_file(args.env_file, override=True)
    client = init_client()

    questions = load_questions(args.question_csv)
    if args.n > 0:
        questions = questions[: args.n]

    done_indices, baseline_log, _fusion_log = load_resume_state(args)
    questions_to_run = [q for q in questions if q["index"] + 1 not in done_indices]

    if not questions_to_run:
        print("All questions already completed.")
        return 0

    t_all = time.perf_counter()
    pipeline_items, retrieval_state = build_pipeline_items(args, questions_to_run)
    questions_run = run_generation_loop(
        args, client, pipeline_items, retrieval_state, baseline_log
    )

    elapsed = time.perf_counter() - t_all
    print("\nDONE")
    print(f"Questions run:   {questions_run}")
    print(f"Baseline CSV:    {args.output_csv}")
    print(f"Baseline JSON:   {args.output_json}")
    print(f"Wall time:       {elapsed:.1f}s ({elapsed / 60:.1f} min)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
