"""
module3_split.py

Split master_dataset.jsonl → train/test 80/20
Stratify theo intent, giữ index=363 cùng split.

Output:
  train_dataset.jsonl   (~629 queries, full negatives)
  test_dataset.jsonl    (~157 queries, full negatives)
  train_stage1.jsonl    synthesized only       (~1,291 triplets)
  train_stage2.jsonl    synthesized+extra_synth (~4,767 triplets)
  train_stage3.jsonl    all, mined capped 5/query (~7,300 triplets)

"""

import json
import random
import argparse
import logging
from pathlib import Path
from collections import Counter, defaultdict

log = logging.getLogger(__name__)

SEED       = 42
TEST_RATIO = 0.20
MINED_CAP  = 10   # max mined negatives per query ở stage 3
PIPELINE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MASTER_PATH = PIPELINE_ROOT / "master_dataset.jsonl"
DEFAULT_OUT_DIR = PIPELINE_ROOT


# ─── Load ─────────────────────────────────────────────────────────────────────

def load_master(path: Path) -> list[dict]:
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    log.info(f"Loaded {len(records)} records from {path.name}")
    return records


# ─── Split ────────────────────────────────────────────────────────────────────

def split_train_test(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Stratified split theo intent, giữ index=363 cùng split.
    """
    rng = random.Random(SEED)

    # Group theo intent
    by_intent = defaultdict(list)
    for rec in records:
        by_intent[rec.get("intent", "unknown")].append(rec)

    train, test = [], []

    for intent, recs in by_intent.items():
        recs_copy = recs[:]
        rng.shuffle(recs_copy)

        n_test = max(1, round(len(recs_copy) * TEST_RATIO))
        test  += recs_copy[:n_test]
        train += recs_copy[n_test:]

    # Đảm bảo index=363 (dup) cùng split
    # Tìm xem 363 đang ở đâu
    idx363_train = [r for r in train if r["index"] == 363]
    idx363_test  = [r for r in test  if r["index"] == 363]

    if idx363_train and idx363_test:
        # Move tất cả về train
        for r in idx363_test:
            test.remove(r)
            train.append(r)
        log.info("index=363: moved all records to train")

    log.info(f"Split: train={len(train)} | test={len(test)}")
    return train, test


# ─── Build triplets từ master record ─────────────────────────────────────────

def _make_triplets(
    records:         list[dict],
    include_synth:   bool = True,
    include_extra:   bool = True,
    include_mined:   bool = True,
    mined_cap:       int  = 999,
) -> list[dict]:
    """
    Explode master records thành flat triplets.
    Mỗi (query, positive, negative) = 1 triplet.
    Với query có nhiều positives: pair mỗi negative với positive tương ứng
    (synthesized → paired_positive_chunk_id, mined/extra → positive bge cao nhất).
    """
    triplets = []

    for rec in records:
        query         = rec["query"]
        positives     = rec["positives"]
        negatives     = rec["negatives"]
        bge_score_pos = rec["bge_score_pos"]

        if not positives or not negatives:
            continue

        # Default positive = positive có bge_score cao nhất
        best_positive = max(positives, key=lambda p: p["bge_score"])

        # Build chunk_id → positive text map (cho synthesized pairing)
        pos_by_id = {p["chunk_id"]: p for p in positives}

        mined_count = 0

        for neg in negatives:
            neg_type = neg["type"]

            # Filter theo stage
            if neg_type == "synthesized" and not include_synth:
                continue
            if neg_type == "extra_synth" and not include_extra:
                continue
            if neg_type == "mined":
                if not include_mined:
                    continue
                if mined_count >= mined_cap:
                    continue
                mined_count += 1

            # Chọn positive tương ứng
            paired_id = neg.get("paired_positive_chunk_id")
            if paired_id and paired_id in pos_by_id:
                pos = pos_by_id[paired_id]
            else:
                pos = best_positive

            triplets.append({
                "query":          query,
                "positive":       pos["text"],
                "negative":       neg["text"],
                "neg_type":       neg_type,
                "edit_type":      neg.get("edit_type"),
                "bge_score_pos":  bge_score_pos,
                "bge_score_neg":  neg.get("bge_score_neg"),
                "gap":            neg.get("gap"),
                "index":          rec["index"],
                "intent":         rec["intent"],
            })

    return triplets


# ─── Build curriculum stages ──────────────────────────────────────────────────

def build_curriculum_stages(train: list[dict]) -> dict[str, list[dict]]:
    """
    Stage 1: synthesized only
    Stage 2: synthesized + extra_synth
    Stage 3: all sources, mined capped MINED_CAP/query
    """
    stages = {
        "stage1": _make_triplets(train,
            include_synth=True, include_extra=False, include_mined=False),
        # "stage2": _make_triplets(train,
        #     include_synth=True, include_extra=True,  include_mined=False),
        "stage2": _make_triplets(train,
            include_synth=True, include_extra=True,  include_mined=True,
            mined_cap=MINED_CAP),
    }
    return stages


# ─── Write ────────────────────────────────────────────────────────────────────

def write_jsonl(records: list[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ─── Report ───────────────────────────────────────────────────────────────────

def print_report(
    train:    list[dict],
    test:     list[dict],
    stages:   dict[str, list[dict]],
    out_dir:  Path,
):
    def intent_dist(records):
        c = Counter(r.get("intent", "?") for r in records)
        return " | ".join(f"{k}:{v}" for k, v in sorted(c.items()))

    def neg_dist(triplets):
        c = Counter(t["neg_type"] for t in triplets)
        return " | ".join(f"{k}:{v}" for k, v in sorted(c.items()))

    print("\n" + "=" * 60)
    print("MODULE 3 — SPLIT REPORT")
    print("=" * 60)
    print(f"  train queries : {len(train):>5}  ({intent_dist(train)})")
    print(f"  test  queries : {len(test):>5}  ({intent_dist(test)})")
    print()
    print("  Curriculum stages (train only):")
    for name, triplets in stages.items():
        print(f"    {name}: {len(triplets):>6} triplets  [{neg_dist(triplets)}]")
    print()
    print("  Output files:")
    for fname in ["train_dataset.jsonl", "test_dataset.jsonl",
                  "train_stage1.jsonl", "train_stage2.jsonl"]:
        p = out_dir / fname
        if p.exists():
            print(f"    {fname}")
    print("=" * 60)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--master",  default=DEFAULT_MASTER_PATH)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    args   = parser.parse_args()

    out_dir = Path(args.out_dir)
    records = load_master(Path(args.master))

    # Split
    train, test = split_train_test(records)

    # Curriculum stages từ train
    stages = build_curriculum_stages(train)

    # Write
    write_jsonl(train,           out_dir / "train_dataset.jsonl")
    write_jsonl(test,            out_dir / "test_dataset.jsonl")
    write_jsonl(stages["stage1"], out_dir / "train_stage1.jsonl")
    write_jsonl(stages["stage2"], out_dir / "train_stage2.jsonl")
    # write_jsonl(stages["stage3"], out_dir / "train_stage3.jsonl")

    print_report(train, test, stages, out_dir)


if __name__ == "__main__":
    main()
