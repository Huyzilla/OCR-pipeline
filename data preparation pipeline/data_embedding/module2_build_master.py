"""
module2_build_master.py

Gộp tất cả nguồn data vào 1 record per query.
Index authoritative = row number từ question.csv.

Output: master_dataset.jsonl
  Mỗi dòng = 1 query với đầy đủ positives + negatives từ 3 nguồn.

Usage:
    from module2_build_master import build_master
    build_master(data, out_path="master_dataset.jsonl")
"""

import json
import logging
from pathlib import Path
from collections import Counter

log = logging.getLogger(__name__)

try:
    from .module1_load_validate import (
        DEFAULT_EXTRA_SYNTH_PATH,
        DEFAULT_JUDGED_PATH,
        DEFAULT_QUESTIONS_PATH,
        DEFAULT_RETRIEVE_PATH,
        DEFAULT_SYNTH_PATH,
        PIPELINE_ROOT,
        load_all,
    )
except ImportError:
    from module1_load_validate import (
        DEFAULT_EXTRA_SYNTH_PATH,
        DEFAULT_JUDGED_PATH,
        DEFAULT_QUESTIONS_PATH,
        DEFAULT_RETRIEVE_PATH,
        DEFAULT_SYNTH_PATH,
        PIPELINE_ROOT,
        load_all,
    )

# Rank range cho mined negatives
MINED_RANK_MIN = 5
MINED_RANK_MAX = 15
DEFAULT_MASTER_PATH = PIPELINE_ROOT / "master_dataset.jsonl"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_positive_chunk_ids(judged_rec: dict) -> set[str]:
    """chunk_ids của gold chunks."""
    top5 = judged_rec.get("top5_candidates", [])
    return {
        top5[i]["chunk_id"]
        for i in judged_rec.get("gold_indices", [])
        if i < len(top5)
    }


def _get_partial_chunk_ids(judged_rec: dict) -> set[str]:
    """chunk_ids của partial chunks — không dùng làm negative."""
    top5 = judged_rec.get("top5_candidates", [])
    return {
        top5[i]["chunk_id"]
        for i in judged_rec.get("partial_indices", [])
        if i < len(top5)
    }


def _build_positives(judged_rec: dict) -> list[dict]:
    """
    Trả về list positives:
    [{"chunk_id": ..., "text": ..., "bge_score": ...}]
    """
    top5      = judged_rec.get("top5_candidates", [])
    gold_idxs = judged_rec.get("gold_indices", [])
    positives = []
    for i in gold_idxs:
        if i < len(top5):
            c = top5[i]
            positives.append({
                "chunk_id":  c["chunk_id"],
                "text":      c["chunk"],
                "bge_score": c["bge_score"],
            })
    return positives


def _build_negatives_synth(synth_recs: list[dict]) -> list[dict]:
    """
    Từ synth records (có thể >1 vì dup index=363).
    Mỗi valid_negative → 1 negative entry.
    """
    negatives = []
    for rec in synth_recs:
        pos_chunk_id = rec.get("positive_chunk_id", "")
        for neg in rec.get("valid_negatives", []):
            # Chỉ lấy negatives đã pass self-check
            if neg.get("answers_query", False):
                continue
            if neg.get("contains_giveaway_style", False):
                continue
            text = neg.get("text", "").strip()
            if not text:
                continue
            negatives.append({
                "text":          text,
                "type":          "synthesized",
                "edit_type":     neg.get("edit_type"),
                "bge_score_neg": None,   # không có score thật
                "paired_positive_chunk_id": pos_chunk_id,
            })
    return negatives


def _build_negatives_mined(
    retrieve_rec:      dict,
    exclude_chunk_ids: set[str],
    bge_score_pos:     float | None,
) -> list[dict]:
    """
    Từ retrieve candidates rank MINED_RANK_MIN..MINED_RANK_MAX.
    Loại bỏ: gold chunks, partial chunks.
    Loại bỏ: rank 4 nếu không rõ ràng irrelevant (đã xử lý trước khi gọi hàm này).
    """
    negatives = []
    for cand in retrieve_rec.get("candidates", []):
        rank     = cand.get("rank", 99)
        chunk_id = cand.get("chunk_id", "")
        text     = cand.get("chunk", "").strip()
        score    = cand.get("bge_score", 0.0)

        if rank < MINED_RANK_MIN or rank > MINED_RANK_MAX:
            continue
        if chunk_id in exclude_chunk_ids:
            continue
        if not text:
            continue

        gap = (bge_score_pos - score) if bge_score_pos is not None else None

        negatives.append({
            "text":          text,
            "type":          "mined",
            "edit_type":     None,
            "bge_score_neg": round(score, 4),
            "gap":           round(gap, 4) if gap is not None else None,
            "rank":          rank,
        })
    return negatives


def _build_negatives_extra(extra_recs: list[dict]) -> list[dict]:
    """Từ extra_synth records."""
    negatives = []
    for rec in extra_recs:
        text = rec.get("negative", "").strip()
        if not text:
            continue
        negatives.append({
            "text":          text,
            "type":          "extra_synth",
            "edit_type":     None,
            "bge_score_neg": None,
        })
    return negatives


# ─── Build rank-4 eligible ────────────────────────────────────────────────────

def _rank4_is_eligible(judged_rec: dict) -> str | None:
    """
    Rank 4 (index 4 trong top5_candidates) dùng làm negative
    nếu không nằm trong gold_indices và partial_indices.
    Returns chunk_id nếu eligible, else None.
    """
    top5          = judged_rec.get("top5_candidates", [])
    gold_set      = set(judged_rec.get("gold_indices", []))
    partial_set   = set(judged_rec.get("partial_indices", []))
    if 4 not in gold_set and 4 not in partial_set and len(top5) > 4:
        return top5[4]["chunk_id"]
    return None


# ─── Core build function ──────────────────────────────────────────────────────

def build_master(data: dict, out_path: str | Path = DEFAULT_MASTER_PATH) -> list[dict]:
    """
    data: output từ module1_load_validate.load_all()

    Returns list of master records (cũng ghi ra file).
    """
    questions        = data["questions"]        # {index: question_text}
    judged           = data["judged"]           # {index: [record]}
    synth            = data["synth"]            # {index: [record]}
    retrieve         = data["retrieve"]         # {index: record}
    extra_synth      = data["extra_synth"]      # {index: [record]}
    eligible_indices = data["eligible_indices"] # set[int]

    master   = []
    neg_stats = Counter()

    for idx in sorted(eligible_indices):
        # ── Index authoritative từ question.csv ───────────────────────────────
        query_text = questions.get(idx, "").strip()
        if not query_text:
            log.warning(f"index={idx}: không có question text, bỏ qua")
            continue

        # ── Judged record ─────────────────────────────────────────────────────
        judged_recs = judged.get(idx, [])
        if not judged_recs:
            log.warning(f"index={idx}: không có judged record, bỏ qua")
            continue
        judged_rec = judged_recs[0]  # judged không dup (ngoài edge case đã xử lý)

        intent = judged_rec.get("intent", "")

        # ── Positives ─────────────────────────────────────────────────────────
        positives = _build_positives(judged_rec)
        if not positives:
            continue  # không có positive → không thể build triplet

        # bge_score_pos = score của positive có score cao nhất
        bge_score_pos = max(p["bge_score"] for p in positives)

        # ── Chunk IDs cần exclude khỏi negatives ──────────────────────────────
        pos_chunk_ids     = _get_positive_chunk_ids(judged_rec)
        partial_chunk_ids = _get_partial_chunk_ids(judged_rec)
        exclude_ids       = pos_chunk_ids | partial_chunk_ids

        # ── Negatives từ 3 nguồn ──────────────────────────────────────────────
        negatives = []

        # 1. Synthesized (từ synth file)
        synth_recs  = synth.get(idx, [])
        synth_negs  = _build_negatives_synth(synth_recs)
        negatives  += synth_negs
        neg_stats["synthesized"] += len(synth_negs)

        # 2. Mined (từ retrieve rank 5-15, + rank 4 nếu eligible)
        retrieve_rec = retrieve.get(idx, {})
        mined_negs   = _build_negatives_mined(retrieve_rec, exclude_ids, bge_score_pos)

        # Rank 4: thêm nếu không phải gold/partial
        if _rank4_is_eligible(judged_rec):
            top5  = judged_rec.get("top5_candidates", [])
            cand4 = top5[4]
            if cand4["chunk_id"] not in exclude_ids and cand4.get("chunk", "").strip():
                gap = bge_score_pos - cand4["bge_score"]
                mined_negs.append({
                    "text":          cand4["chunk"],
                    "type":          "mined",
                    "edit_type":     None,
                    "bge_score_neg": round(cand4["bge_score"], 4),
                    "gap":           round(gap, 4),
                    "rank":          4,
                })

        negatives  += mined_negs
        neg_stats["mined"] += len(mined_negs)

        # 3. Extra synth
        extra_recs  = extra_synth.get(idx, [])
        extra_negs  = _build_negatives_extra(extra_recs)
        negatives  += extra_negs
        neg_stats["extra_synth"] += len(extra_negs)

        # ── Assemble record ───────────────────────────────────────────────────
        master.append({
            "index":              idx,
            "query":              query_text,   # authoritative từ question.csv
            "intent":             intent,
            "positives":          positives,
            "negatives":          negatives,
            "partial_chunk_ids":  sorted(partial_chunk_ids),
            "n_positives":        len(positives),
            "n_negatives":        len(negatives),
            "n_neg_synth":        len(synth_negs),
            "n_neg_mined":        len(mined_negs),
            "n_neg_extra":        len(extra_negs),
            "bge_score_pos":      round(bge_score_pos, 4),
        })

    # ── Write output ──────────────────────────────────────────────────────────
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for rec in master:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    _print_summary(master, neg_stats, out_path)
    return master


# ─── Summary ──────────────────────────────────────────────────────────────────

def _print_summary(master: list[dict], neg_stats: Counter, out_path: Path):
    total_negs = sum(r["n_negatives"] for r in master)
    no_neg     = [r["index"] for r in master if r["n_negatives"] == 0]

    n_pos_dist = Counter(r["n_positives"] for r in master)
    n_neg_dist = {
        "0":    sum(1 for r in master if r["n_negatives"] == 0),
        "1-3":  sum(1 for r in master if 1 <= r["n_negatives"] <= 3),
        "4-9":  sum(1 for r in master if 4 <= r["n_negatives"] <= 9),
        "10+":  sum(1 for r in master if r["n_negatives"] >= 10),
    }

    print("\n" + "=" * 55)
    print("MODULE 2 — MASTER DATASET REPORT")
    print("=" * 55)
    print(f"  Records           : {len(master):>5}  queries")
    print(f"  Total negatives   : {total_negs:>5}")
    print()
    print("  Negative sources:")
    for src, count in neg_stats.items():
        print(f"    {src:<20}: {count:>5}")
    print()
    print("  Positives per query:")
    for k in sorted(n_pos_dist):
        print(f"    {k} positive(s)    : {n_pos_dist[k]:>5} queries")
    print()
    print("  Negatives per query:")
    for k, v in n_neg_dist.items():
        print(f"    {k:<8}           : {v:>5} queries")
    if no_neg:
        print(f"\n  ⚠ {len(no_neg)} queries không có negative nào: {no_neg[:10]}")
    print()
    print(f"  Output            : {out_path}")
    print("=" * 55)


# ─── Standalone ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--questions",   default=DEFAULT_QUESTIONS_PATH)
    parser.add_argument("--judged",      default=DEFAULT_JUDGED_PATH)
    parser.add_argument("--synth",       default=DEFAULT_SYNTH_PATH)
    parser.add_argument("--retrieve",    default=DEFAULT_RETRIEVE_PATH)
    parser.add_argument("--extra-synth", default=DEFAULT_EXTRA_SYNTH_PATH)
    parser.add_argument("--out",         default=DEFAULT_MASTER_PATH)
    args = parser.parse_args()

    data = load_all(
        questions_path   = args.questions,
        judged_path      = args.judged,
        synth_path       = args.synth,
        retrieve_path    = args.retrieve,
        extra_synth_path = args.extra_synth,
        verbose          = False,
    )
    build_master(data, out_path=args.out)
