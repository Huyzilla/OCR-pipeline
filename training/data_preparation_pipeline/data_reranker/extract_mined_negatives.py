#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract mined negatives từ rank 4-20 trong gold_chunks_judged.jsonl.
Tính BGE score gap, gán hardness band.

Rules:
  - GPT confirmed irrelevant (irrelevant_indices): lấy kể cả cùng doc
  - Rank 5-20 chưa GPT phân loại: chỉ lấy khác document với positive
  - Loại gold/partial chunk_ids
  - Gap < 0.1 → discard

Output: domain_data/mined_negatives.jsonl

Usage:
    python extract_mined_negatives.py \
        --judged    domain_data/gold_chunks_judged.jsonl \
        --retrieve  retrieve_rerank_991.jsonl \
        --output    domain_data/mined_negatives.jsonl
"""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def get_hardness_band(gap: float) -> str:
    if gap >= 0.7:   return "easy"
    elif gap >= 0.4: return "medium"
    elif gap >= 0.1: return "hard"
    else:            return "discard"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--judged",   type=Path, required=True)
    parser.add_argument("--retrieve", type=Path, required=True)
    parser.add_argument("--output",   type=Path, required=True)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Load judged
    print(f"Loading: {args.judged}")
    with open(args.judged, encoding="utf-8") as f:
        judged_data = [json.loads(l) for l in f if l.strip()]

    gold_entries = [
        e for e in judged_data
        if e.get("gold_indices")
        and not e.get("error")
        and e.get("status") != "low_score_skip"
    ]
    print(f"  Gold entries: {len(gold_entries)}")

    # Load retrieve — để lấy text rank 5-20
    print(f"Loading: {args.retrieve}")
    retrieve_text_map: dict[int, dict[str, str]] = {}
    with open(args.retrieve, encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            retrieve_text_map[e["index"]] = {
                c["chunk_id"]: c["chunk"]
                for c in e.get("candidates", [])
            }
    print(f"  Loaded {len(retrieve_text_map):,} entries")

    # Process
    out_f   = open(args.output, "w", encoding="utf-8")
    stats   = defaultdict(int)
    bands   = Counter()

    for entry in gold_entries:
        idx          = entry["index"]
        question     = entry["question"]
        intent       = entry["intent"]
        top5         = entry.get("top5_candidates", [])
        all_meta     = entry.get("all_candidates_meta", [])
        gold_indices = entry["gold_indices"]
        irr_indices  = entry.get("irrelevant_indices", [])

        # Positive
        gi        = gold_indices[0]
        if gi >= len(top5):
            continue
        positive    = top5[gi]["chunk"]
        pos_score   = top5[gi]["bge_score"]
        pos_chunk_id = top5[gi]["chunk_id"]
        pos_doc     = pos_chunk_id.split("::")[0]

        # Excluded chunk_ids (gold + partial)
        excluded_ids = set()
        for i in gold_indices + entry.get("partial_indices", []):
            if i < len(top5):
                excluded_ids.add(top5[i]["chunk_id"])

        # GPT confirmed irrelevant chunk_ids
        irr_chunk_ids = set()
        for ii in irr_indices:
            if ii < len(top5):
                irr_chunk_ids.add(top5[ii]["chunk_id"])

        # Text map từ retrieve
        idx_text_map = retrieve_text_map.get(idx, {})

        neg_entries = []

        for c in all_meta:
            rank         = c["rank"]
            chunk_id     = c["chunk_id"]
            neg_score    = c["bge_score"]
            chunk_doc    = chunk_id.split("::")[0]

            if rank < 4:
                continue
            if chunk_id in excluded_ids:
                continue

            # Filter logic
            is_gpt_irr   = chunk_id in irr_chunk_ids
            is_cross_doc = chunk_doc != pos_doc

            if not is_gpt_irr and not is_cross_doc:
                # Cùng doc, chưa GPT phân loại → bỏ
                stats["skipped_same_doc"] += 1
                continue

            # BGE score gap
            gap  = pos_score - neg_score
            band = get_hardness_band(gap)
            bands[band] += 1

            if band == "discard":
                stats["discarded_gap"] += 1
                continue

            # Lấy text
            neg_text = idx_text_map.get(chunk_id, "")
            if not neg_text:
                stats["no_text"] += 1
                continue

            neg_entries.append({
                "chunk_id":   chunk_id,
                "rank":       rank,
                "bge_score":  round(neg_score, 4),
                "gap":        round(gap, 4),
                "hardness":   band,
                "source":     "irr_gpt" if is_gpt_irr else "cross_doc",
                "text":       neg_text,
            })
            stats["kept"] += 1

        if neg_entries:
            out_f.write(json.dumps({
                "index":       idx,
                "question":    question,
                "intent":      intent,
                "positive":    positive,
                "pos_chunk_id": pos_chunk_id,
                "pos_score":   round(pos_score, 4),
                "negatives":   neg_entries,
                "n":           len(neg_entries),
            }, ensure_ascii=False) + "\n")

    out_f.close()

    # Stats
    print(f"\n{'='*55}")
    print(f"DONE: {args.output}")
    print(f"  Skipped (same doc, no GPT): {stats['skipped_same_doc']}")
    print(f"  Discarded (gap < 0.1):      {stats['discarded_gap']}")
    print(f"  No text found:              {stats['no_text']}")
    print(f"  Kept:                       {stats['kept']}")
    print(f"\n  Hardness bands:")
    for band in ["easy", "medium", "hard", "discard"]:
        print(f"    {band:<10}: {bands[band]}")

    # Count entries with negatives
    with open(args.output, encoding="utf-8") as f:
        entries = [json.loads(l) for l in f if l.strip()]
    print(f"\n  Entries with negatives: {len(entries)}")
    avg = sum(e["n"] for e in entries) / max(len(entries), 1)
    print(f"  Avg negatives/entry:    {avg:.1f}")


if __name__ == "__main__":
    main()