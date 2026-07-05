from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for path in (start, *start.parents):
        if (path / ".git").exists():
            return path
    return start


ROOT_DIR = find_repo_root(Path(__file__).resolve())
DEFAULT_QUESTION_PATH = ROOT_DIR / "data" / "question.json"
DEFAULT_CHUNK_DIR = ROOT_DIR / "chunk_outputs1_finals"
DEFAULT_OUTPUT_PATH = ROOT_DIR / "data" / "question_gold_corpus.jsonl"


def load_questions(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Question file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        records = json.load(f)

    if not isinstance(records, list):
        raise ValueError(f"Expected a JSON list in {path}")

    return records


def load_chunk_corpus(chunk_dir: Path) -> dict[str, str]:
    if not chunk_dir.exists():
        raise FileNotFoundError(f"Chunk directory not found: {chunk_dir}")

    chunk_files = sorted(chunk_dir.glob("*/*_chunks*.json"))
    if not chunk_files:
        chunk_files = sorted(chunk_dir.glob("*/*.json"))

    if not chunk_files:
        raise FileNotFoundError(f"No chunk JSON files found under {chunk_dir}")

    corpus: dict[str, str] = {}
    for chunk_file in chunk_files:
        doc_scope = chunk_file.parent.name
        with chunk_file.open("r", encoding="utf-8") as f:
            records = json.load(f)

        if not isinstance(records, list):
            raise ValueError(f"Expected a JSON list in {chunk_file}")

        for i, item in enumerate(records):
            if not isinstance(item, dict):
                continue

            text = str(item.get("page_content", "")).strip()
            if not text:
                continue

            metadata = item.get("metadata", {})
            metadata = metadata if isinstance(metadata, dict) else {}
            raw_chunk_id = metadata.get("chunk_id") or f"chunk::{metadata.get('chunk_index', i)}"
            raw_chunk_id = str(raw_chunk_id).strip()
            if not raw_chunk_id:
                continue

            if raw_chunk_id.startswith(f"{doc_scope}::"):
                chunk_id = raw_chunk_id
            else:
                chunk_id = f"{doc_scope}::{raw_chunk_id}"

            corpus[chunk_id] = text

    return corpus


def build_question_mapping(
    questions: list[dict[str, Any]],
    corpus: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    mapped_records: list[dict[str, Any]] = []
    missing_records: list[dict[str, Any]] = []

    for index, record in enumerate(questions, start=1):
        gold_chunk_ids = [
            str(chunk_id).strip()
            for chunk_id in record.get("gold_chunk_ids", [])
            if str(chunk_id).strip()
        ]
        gold_chunks = [
            {"chunk_id": chunk_id, "text": corpus[chunk_id]}
            for chunk_id in gold_chunk_ids
            if chunk_id in corpus
        ]
        missing_chunk_ids = [
            chunk_id for chunk_id in gold_chunk_ids if chunk_id not in corpus
        ]

        if missing_chunk_ids:
            missing_records.append(
                {
                    "index": index,
                    "question": record.get("question", ""),
                    "missing_gold_chunk_ids": missing_chunk_ids,
                }
            )

        mapped_records.append(
            {
                "index": index,
                "question": record.get("question", ""),
                "options": record.get("options", {}),
                "answer": record.get("answer", ""),
                "difficulty": record.get("difficulty", ""),
                "gold_chunk_ids": gold_chunk_ids,
                "gold_chunks": gold_chunks,
            }
        )

    return mapped_records, missing_records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Map gold chunk text from chunk_outputs1_finals into data/question.json."
    )
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTION_PATH)
    parser.add_argument("--chunk-dir", type=Path, default=DEFAULT_CHUNK_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    questions = load_questions(args.questions)
    corpus = load_chunk_corpus(args.chunk_dir)
    mapped_records, missing_records = build_question_mapping(questions, corpus)

    print(f"Questions: {len(questions)}")
    print(f"Corpus chunks: {len(corpus)}")
    print(f"Questions with missing gold chunks: {len(missing_records)}")

    if missing_records:
        preview = missing_records[:5]
        raise ValueError(f"Missing gold chunks. Preview: {preview}")

    if args.dry_run:
        print(f"Dry run only. Output would be: {args.output}")
        return

    write_jsonl(args.output, mapped_records)
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
