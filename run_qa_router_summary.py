#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from qa.openai_client import load_env_file
from qa.question_io import load_router_questions
from qa.utils import load_all_chunks


DATA_DIR = Path("data")
QUESTION_CSV = DATA_DIR / "question.csv"
CHUNK_DIR = Path("chunk_outputs_finals")
DOC_INDEX_DIR = Path("doc_index")

ROUTER_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "AITeamVN/Vietnamese_Embedding_v2"
RERANK_MODEL = "BAAI/bge-reranker-v2-m3"
ANSWER_MODEL = "gpt-4o-mini"


def run_qa_pipeline(
    question_csv: Path,
    chunk_dir: Path,
    doc_index_dir: Path = DOC_INDEX_DIR,
    output_json: Path | None = None,
    output_csv: Path | None = None,
    max_questions: int = 0,
    router_model: str = ROUTER_MODEL,
    embedding_model: str = EMBEDDING_MODEL,
    rerank_model: str = RERANK_MODEL,
    answer_model: str = ANSWER_MODEL,
    context_debug: bool = False,
):
    print("\n" + "=" * 70)
    print("QA Pipeline - Router-Summary Approach")
    print("=" * 70)

    start_time = datetime.now()

    all_questions = load_router_questions(question_csv)
    if max_questions > 0:
        questions = all_questions[:max_questions]
        print(f"Processing {len(questions)}/{len(all_questions)} questions")
    else:
        questions = all_questions
        print(f"Processing all {len(questions)} questions")

    print(f"\nLoading chunks from {chunk_dir}...")
    all_chunks = load_all_chunks(chunk_dir)
    print(f"Loaded {len(all_chunks)} chunks")

    print("\nInitializing QA pipeline...")
    from pipeline_router_summary import create_qa_pipeline

    pipeline = create_qa_pipeline(
        all_chunks=all_chunks,
        doc_index_dir=doc_index_dir,
        embedding_model=embedding_model,
        rerank_model=rerank_model,
        router_model=router_model,
        answer_model=answer_model,
    )

    print("\nProcessing questions...")
    results = pipeline.process_batch(
        questions,
        output_json=output_json,
        output_csv=output_csv,
        context_debug=context_debug and len(questions) > 0,
    )

    elapsed = datetime.now() - start_time
    total = len(results)

    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"Total questions: {total}")
    print(f"Time elapsed: {elapsed}")
    if total:
        print(f"Time per question: {elapsed.total_seconds() / total:.1f}s")

    has_truth = sum(1 for r in results if r["truth"] is not None)
    if has_truth > 0:
        correct = sum(1 for r in results if r["is_correct"] is True)
        print(f"Accuracy: {correct}/{has_truth} ({correct / has_truth * 100:.1f}%)")

        by_intent = {}
        for r in results:
            if r["truth"] is None:
                continue
            intent = r["intent"]
            if intent not in by_intent:
                by_intent[intent] = {"total": 0, "correct": 0}
            by_intent[intent]["total"] += 1
            if r["is_correct"]:
                by_intent[intent]["correct"] += 1

        print("\nAccuracy by intent:")
        for intent, stats in by_intent.items():
            if stats["total"] > 0:
                pct = stats["correct"] / stats["total"] * 100
                print(f"  {intent}: {stats['correct']}/{stats['total']} ({pct:.1f}%)")

    print("\nPipeline completed.")
    return results


def default_output_paths() -> tuple[Path, Path]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(f"results_{timestamp}.json"), Path(f"results_{timestamp}.csv")


def print_dry_run(args) -> None:
    print("Dry run configuration")
    print(f"  question_csv   : {args.question_csv}")
    print(f"  chunk_dir      : {args.chunk_dir}")
    print(f"  doc_index_dir  : {args.doc_index_dir}")
    print(f"  output_json    : {args.output_json}")
    print(f"  output_csv     : {args.output_csv}")
    print(f"  max_questions  : {args.max_questions}")
    print(f"  router_model   : {args.router_model}")
    print(f"  embedding_model: {args.embedding_model}")
    print(f"  rerank_model   : {args.rerank_model}")
    print(f"  answer_model   : {args.answer_model}")
    print(f"  debug          : {args.debug}")


def parse_args():
    parser = argparse.ArgumentParser(description="QA Pipeline - Router-Summary Approach")
    parser.add_argument("--question-csv", type=Path, default=QUESTION_CSV)
    parser.add_argument("--chunk-dir", type=Path, default=CHUNK_DIR)
    parser.add_argument("--doc-index-dir", type=Path, default=DOC_INDEX_DIR)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--output-csv", type=Path, default=None)
    parser.add_argument("--max-questions", type=int, default=0)
    parser.add_argument("--n", type=int, default=None)
    parser.add_argument("--router-model", default=ROUTER_MODEL)
    parser.add_argument("--embedding-model", default=EMBEDDING_MODEL)
    parser.add_argument("--rerank-model", default=RERANK_MODEL)
    parser.add_argument("--answer-model", default=ANSWER_MODEL)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--no-env-file", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.n is not None:
        args.max_questions = args.n

    default_json, default_csv = default_output_paths()
    if args.output_json is None:
        args.output_json = default_json
    if args.output_csv is None:
        args.output_csv = default_csv
    return args


def main() -> int:
    args = parse_args()

    if args.dry_run:
        print_dry_run(args)
        return 0

    if not args.question_csv.exists():
        print(f"Error: Question file not found: {args.question_csv}")
        return 1
    if not args.chunk_dir.exists():
        print(f"Error: Chunk directory not found: {args.chunk_dir}")
        return 1

    if not args.no_env_file:
        load_env_file(args.env_file, override=True)

    try:
        run_qa_pipeline(
            question_csv=args.question_csv,
            chunk_dir=args.chunk_dir,
            doc_index_dir=args.doc_index_dir,
            output_json=args.output_json,
            output_csv=args.output_csv,
            max_questions=args.max_questions,
            router_model=args.router_model,
            embedding_model=args.embedding_model,
            rerank_model=args.rerank_model,
            answer_model=args.answer_model,
            context_debug=args.debug,
        )
        return 0
    except Exception as exc:
        print(f"\nError: {exc}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
