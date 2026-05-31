#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge synthesized (filtered) + mined negatives → final training triplets.

Capping:
  - easy:   max N per entry (default 2)
  - medium: giữ hết
  - hard:   giữ hết
  - synthesized: giữ hết (đã hard by definition)

Output:
  domain_data/domain_train_final_train.jsonl
  domain_data/domain_train_final_dev.jsonl

Usage:
    python merge_training_data.py \
        --synthesized  domain_data/synthesized_negatives_answerability_filtered.jsonl \
        --mined        domain_data/mined_negatives.jsonl \
        --output-dir   domain_data/ \
        [--max-easy    2]
"""

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthesized", type=Path, required=True)
    parser.add_argument("--mined",       type=Path, required=True)
    parser.add_argument("--output-dir",  type=Path, default=Path("domain_data"))
    parser.add_argument("--max-easy",    type=int,  default=2,
                        help="Max easy negatives per entry (default 2)")
    parser.add_argument("--dev-ratio",   type=float, default=0.1)
    parser.add_argument("--seed",        type=int,   default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # ── Load synthesized (filtered) ───────────────────────────────────────────
    print(f"Loading synthesized: {args.synthesized}")
    with open(args.synthesized, encoding="utf-8") as f:
        synth_data = [json.loads(l) for l in f if l.strip()]

    # Index map
    synth_map = {e["index"]: e for e in synth_data}
    print(f"  Entries: {len(synth_map)}")

    # ── Load mined ────────────────────────────────────────────────────────────
    print(f"Loading mined: {args.mined}")
    with open(args.mined, encoding="utf-8") as f:
        mined_data = [json.loads(l) for l in f if l.strip()]

    mined_map = {e["index"]: e for e in mined_data}
    print(f"  Entries: {len(mined_map)}")

    # ── Merge ─────────────────────────────────────────────────────────────────
    all_indices = sorted(set(list(synth_map.keys()) + list(mined_map.keys())))
    print(f"\nTotal unique queries: {len(all_indices)}")

    all_triplets = []
    stats = defaultdict(int)
    band_counter = Counter()

    for idx in all_indices:
        synth_entry = synth_map.get(idx)
        mined_entry = mined_map.get(idx)

        # Lấy positive từ mined (có đầy đủ info) hoặc synth
        if mined_entry:
            positive  = mined_entry["positive"]
            question  = mined_entry["question"]
            intent    = mined_entry["intent"]
        elif synth_entry:
            positive  = synth_entry["positive"]
            question  = synth_entry["question"]
            intent    = synth_entry["intent"]
        else:
            continue

        triplets_for_entry = []

        # ── Synthesized negatives (tất cả là hard) ───────────────────────────
        if synth_entry:
            for neg in synth_entry.get("valid_negatives", []):
                neg_text = neg.get("text", "")
                if not neg_text:
                    continue
                triplets_for_entry.append({
                    "query":      question,
                    "positive":   positive,
                    "negative":   neg_text,
                    "neg_source": "synthesized",
                    "edit_type":  neg.get("edit_type", ""),
                    "hardness":   "hard",
                })
                stats["synth"] += 1
                band_counter["hard"] += 1

        # ── Mined negatives ───────────────────────────────────────────────────
        if mined_entry:
            negatives = mined_entry.get("negatives", [])

            # Phân loại theo band
            hard_negs   = [n for n in negatives if n["hardness"] == "hard"]
            medium_negs = [n for n in negatives if n["hardness"] == "medium"]
            easy_negs   = [n for n in negatives if n["hardness"] == "easy"]

            # Shuffle trước khi cap
            random.shuffle(easy_negs)

            # Cap easy
            easy_capped = easy_negs[:args.max_easy]

            for neg_list, label in [
                (hard_negs,    "hard"),
                (medium_negs,  "medium"),
                (easy_capped,  "easy"),
            ]:
                for neg in neg_list:
                    triplets_for_entry.append({
                        "query":      question,
                        "positive":   positive,
                        "negative":   neg["text"],
                        "neg_source": neg.get("source", "mined"),
                        "chunk_id":   neg.get("chunk_id", ""),
                        "bge_score":  neg.get("bge_score", 0),
                        "gap":        neg.get("gap", 0),
                        "hardness":   label,
                    })
                    stats[f"mined_{label}"] += 1
                    band_counter[label] += 1

        all_triplets.extend(triplets_for_entry)

    # ── Stats ─────────────────────────────────────────────────────────────────
    print(f"\nTriplets breakdown:")
    print(f"  Synthesized hard : {stats['synth']}")
    print(f"  Mined hard       : {stats['mined_hard']}")
    print(f"  Mined medium     : {stats['mined_medium']}")
    print(f"  Mined easy       : {stats['mined_easy']}")
    print(f"  Total            : {len(all_triplets)}")
    print(f"\nHardness distribution:")
    total = len(all_triplets)
    for band in ["hard", "medium", "easy"]:
        n = band_counter[band]
        print(f"  {band:<8}: {n:>5} ({n/total*100:.1f}%)")

    # ── Split train/dev theo query (không leak) ───────────────────────────────
    queries = list(set(t["query"] for t in all_triplets))
    random.shuffle(queries)
    n_dev_q  = max(50, int(len(queries) * args.dev_ratio))
    dev_qs   = set(queries[:n_dev_q])
    train_qs = set(queries[n_dev_q:])

    train_triplets = [t for t in all_triplets if t["query"] in train_qs]
    dev_triplets   = [t for t in all_triplets if t["query"] in dev_qs]

    random.shuffle(train_triplets)
    random.shuffle(dev_triplets)

    # ── Save ──────────────────────────────────────────────────────────────────
    train_path = args.output_dir / "domain_train_final_train.jsonl"
    dev_path   = args.output_dir / "domain_train_final_dev.jsonl"

    with open(train_path, "w", encoding="utf-8") as f:
        for t in train_triplets:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    with open(dev_path, "w", encoding="utf-8") as f:
        for t in dev_triplets:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    print(f"\n{'='*55}")
    print(f"  Train: {len(train_triplets):,} triplets → {train_path}")
    print(f"  Dev:   {len(dev_triplets):,} triplets   → {dev_path}")
    print(f"  Split: {len(train_qs)} train queries / {len(dev_qs)} dev queries")


if __name__ == "__main__":
    main()