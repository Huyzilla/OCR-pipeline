#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from _bootstrap import setup_paths

setup_paths()

from qa.openai_client import load_env_file
from pipeline_router_summary.runner import run_qa_pipeline


DATA_DIR = Path("data")
QUESTION_CSV = DATA_DIR / "question.csv"
CHUNK_DIR = Path("chunk_outputs_finals")
DOC_INDEX_DIR = Path("doc_index")

ROUTER_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "AITeamVN/Vietnamese_Embedding_v2"
RERANK_MODEL = "BAAI/bge-reranker-v2-m3"
ANSWER_MODEL = "gpt-4o-mini"

MAX_QUESTIONS = 200
OUTPUT_JSON = Path("router_summary_debug.json")
OUTPUT_CSV = Path("router_summary.csv")
CONTEXT_DEBUG = False
DRY_RUN = False
LOAD_ENV_FILE = True
ENV_FILE = Path(".env")


def print_dry_run() -> None:
    print("Dry run configuration")
    print(f"  question_csv   : {QUESTION_CSV}")
    print(f"  chunk_dir      : {CHUNK_DIR}")
    print(f"  doc_index_dir  : {DOC_INDEX_DIR}")
    print(f"  output_json    : {OUTPUT_JSON}")
    print(f"  output_csv     : {OUTPUT_CSV}")
    print(f"  max_questions  : {MAX_QUESTIONS}")
    print(f"  router_model   : {ROUTER_MODEL}")
    print(f"  embedding_model: {EMBEDDING_MODEL}")
    print(f"  rerank_model   : {RERANK_MODEL}")
    print(f"  answer_model   : {ANSWER_MODEL}")
    print(f"  context_debug  : {CONTEXT_DEBUG}")


def main() -> int:
    if DRY_RUN:
        print_dry_run()
        return 0

    if not QUESTION_CSV.exists():
        print(f"Error: question file not found: {QUESTION_CSV}")
        return 1
    if not CHUNK_DIR.exists():
        print(f"Error: chunk directory not found: {CHUNK_DIR}")
        return 1
    if not DOC_INDEX_DIR.exists():
        print(f"Error: doc index directory not found: {DOC_INDEX_DIR}")
        return 1

    if LOAD_ENV_FILE:
        load_env_file(ENV_FILE, override=True)

    try:
        run_qa_pipeline(
            question_csv=QUESTION_CSV,
            chunk_dir=CHUNK_DIR,
            doc_index_dir=DOC_INDEX_DIR,
            output_json=OUTPUT_JSON,
            output_csv=OUTPUT_CSV,
            max_questions=MAX_QUESTIONS,
            router_model=ROUTER_MODEL,
            embedding_model=EMBEDDING_MODEL,
            rerank_model=RERANK_MODEL,
            answer_model=ANSWER_MODEL,
            context_debug=CONTEXT_DEBUG,
        )
        return 0
    except Exception as exc:
        print(f"\nError: {exc}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
