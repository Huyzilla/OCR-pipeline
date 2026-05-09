#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import io
from pathlib import Path

from pipeline_router_summary import create_qa_pipeline
from qa.utils import load_all_chunks, parse_answer_text
from run_qa_router_summary import load_questions_csv


def format_output_line(answer: str) -> str:
    answers = parse_answer_text(answer)
    if not answers:
        row = [0, ""]
    else:
        row = [len(answers), ",".join(answers)]

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(row)
    return buf.getvalue().rstrip("\r\n")


def load_indices(mismatch_csv: Path) -> list[int]:
    indices: list[int] = []
    with open(mismatch_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw = (row.get("question_index") or "").strip()
            if not raw:
                continue
            idx = int(raw)
            if idx > 0:
                indices.append(idx)
    # Unique + sorted để chạy ổn định
    return sorted(set(indices))


def main() -> int:
    parser = argparse.ArgumentParser(description="Rerun only mismatch questions and update output CSV in-place")
    parser.add_argument("--question-csv", type=Path, default=Path("question.csv"))
    parser.add_argument("--mismatch-csv", type=Path, default=Path("mismatch_question_indices.csv"))
    parser.add_argument("--output-csv", type=Path, default=Path("output_pipeline.csv"))
    parser.add_argument("--chunk-dir", type=Path, default=Path("chunk_outputs_finals"))
    parser.add_argument("--router-model", default="gpt-4o-mini")
    parser.add_argument("--answer-model", default="gpt-4o-mini")
    parser.add_argument("--embedding-model", default="AITeamVN/Vietnamese_Embedding_v2")
    parser.add_argument("--rerank-model", default="BAAI/bge-reranker-v2-m3")
    args = parser.parse_args()

    if not args.question_csv.exists():
        raise FileNotFoundError(f"Question file not found: {args.question_csv}")
    if not args.mismatch_csv.exists():
        raise FileNotFoundError(f"Mismatch file not found: {args.mismatch_csv}")
    if not args.output_csv.exists():
        raise FileNotFoundError(f"Output file not found: {args.output_csv}")
    if not args.chunk_dir.exists():
        raise FileNotFoundError(f"Chunk directory not found: {args.chunk_dir}")

    questions = load_questions_csv(args.question_csv)
    indices = load_indices(args.mismatch_csv)

    with open(args.output_csv, "r", encoding="utf-8") as f:
        output_lines = [line.rstrip("\r\n") for line in f]

    if len(output_lines) < len(questions):
        raise RuntimeError(
            f"output_csv has {len(output_lines)} lines but question_csv has {len(questions)} questions"
        )

    valid_indices = [i for i in indices if 1 <= i <= len(questions)]
    if not valid_indices:
        print("No valid mismatch indices to process.")
        return 0

    print(f"Loading chunks from {args.chunk_dir}...")
    all_chunks = load_all_chunks(args.chunk_dir)
    print(f"Loaded {len(all_chunks)} chunks")

    print("Initializing pipeline...")
    pipeline = create_qa_pipeline(
        all_chunks=all_chunks,
        router_model=args.router_model,
        embedding_model=args.embedding_model,
        rerank_model=args.rerank_model,
        answer_model=args.answer_model,
    )

    total = len(valid_indices)
    print(f"Re-running {total} mismatch questions...")

    for pos, q_idx in enumerate(valid_indices, 1):
        q = questions[q_idx - 1]
        result = pipeline.process_question(
            question=q["question"],
            options=q.get("options"),
            truth=q.get("truth"),
            context_debug=False,
        )
        output_lines[q_idx - 1] = format_output_line(result["answer"])
        print(f"[{pos}/{total}] updated question_index={q_idx} -> {output_lines[q_idx - 1]}")

    with open(args.output_csv, "w", encoding="utf-8", newline="") as f:
        for line in output_lines:
            f.write(line + "\n")

    print(f"Done. Updated {total} lines in {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
