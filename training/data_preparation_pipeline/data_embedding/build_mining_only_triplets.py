"""
Build a flat triplet file that uses only mined negatives.

Default input:
  training/data_preparation_pipeline/train_dataset.jsonl

Default output:
  training/data_preparation_pipeline/train_mining_only.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PIPELINE_ROOT / "train_dataset.jsonl"
DEFAULT_OUTPUT = PIPELINE_ROOT / "train_mining_only.jsonl"


def read_jsonl(path: Path) -> list[dict]:
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def write_jsonl(records: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def make_mining_only_triplets(records: list[dict], mined_cap: int) -> list[dict]:
    triplets = []

    for rec in records:
        positives = rec.get("positives", [])
        negatives = rec.get("negatives", [])
        if not positives or not negatives:
            continue

        best_positive = max(positives, key=lambda p: p.get("bge_score", 0.0))
        mined_count = 0

        for neg in negatives:
            if neg.get("type") != "mined":
                continue
            if mined_count >= mined_cap:
                continue
            mined_count += 1

            triplets.append({
                "query": rec["query"],
                "positive": best_positive["text"],
                "negative": neg["text"],
                "neg_type": "mined",
                "edit_type": neg.get("edit_type"),
                "bge_score_pos": rec.get("bge_score_pos"),
                "bge_score_neg": neg.get("bge_score_neg"),
                "gap": neg.get("gap"),
                "index": rec["index"],
                "intent": rec["intent"],
            })

    return triplets


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--mined-cap", type=int, default=10)
    args = parser.parse_args()

    records = read_jsonl(Path(args.input))
    triplets = make_mining_only_triplets(records, mined_cap=args.mined_cap)
    write_jsonl(triplets, Path(args.output))

    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Mining-only triplets: {len(triplets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
