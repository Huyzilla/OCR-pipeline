"""
module1_load_validate.py

Load 5 file nguồn, validate, trả về các dict sạch + edge case report.

Usage:
    from module1_load_validate import load_all
    data = load_all(
        questions_path   = "data/question.csv",
        judged_path      = "gold_chunks_judged.jsonl",
        synth_path       = "synthesized_negatives.jsonl",
        retrieve_path    = "retrieve_rerank_991.jsonl",
        extra_synth_path = "extra_synthesized.jsonl",
    )
"""

import csv
import json
import logging
from pathlib import Path
from collections import defaultdict

log = logging.getLogger(__name__)

PIPELINE_ROOT = Path(__file__).resolve().parents[1]


def find_repo_root(start: Path) -> Path:
    for path in (start, *start.parents):
        if (path / ".git").exists():
            return path
    return start.parents[2]


REPO_ROOT = find_repo_root(Path(__file__).resolve())
DATA_DIR = REPO_ROOT / "data"
LEGACY_DOMAIN_DATA = REPO_ROOT / "domain_data"


def _first_existing(*paths: Path) -> Path:
    for path in paths:
        if path.exists():
            return path
    return paths[0]


DEFAULT_QUESTIONS_PATH = _first_existing(
    DATA_DIR / "question.csv",
    REPO_ROOT / "question.csv",
    PIPELINE_ROOT / "question.csv",
)
DEFAULT_JUDGED_PATH = _first_existing(
    PIPELINE_ROOT / "gold_chunks_judged.jsonl",
    PIPELINE_ROOT / "domain_data" / "gold_chunks_judged.jsonl",
    LEGACY_DOMAIN_DATA / "gold_chunks_judged.jsonl",
)
DEFAULT_SYNTH_PATH = _first_existing(
    PIPELINE_ROOT / "synthesized_negatives.jsonl",
    PIPELINE_ROOT / "domain_data" / "synthesized_negatives.jsonl",
    LEGACY_DOMAIN_DATA / "synthesized_negatives.jsonl",
)
DEFAULT_RETRIEVE_PATH = _first_existing(
    PIPELINE_ROOT / "retrieve_rerank_991.jsonl",
    PIPELINE_ROOT / "domain_data" / "retrieve_rerank_991.jsonl",
    LEGACY_DOMAIN_DATA / "retrieve_rerank_991.jsonl",
    REPO_ROOT / "retrieve_rerank_991.jsonl",
)
DEFAULT_EXTRA_SYNTH_PATH = _first_existing(
    PIPELINE_ROOT / "extra_synthesized.jsonl",
    PIPELINE_ROOT / "domain_data" / "extra_synthesized.jsonl",
    LEGACY_DOMAIN_DATA / "extra_synthesized.jsonl",
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _read_jsonl(path: Path) -> list[dict]:
    records = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                log.warning(f"{path.name} dòng {i}: JSON lỗi — {e}")
    return records


# ─── Load từng file ────────────────────────────────────────────────────────────

def load_questions(path: Path) -> dict[int, str]:
    """
    question.csv: Question, A, B, C, D
    Returns: {index (1-based row): question_text}
    """
    questions = {}
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            q = row.get("Question", "").strip()
            if q:
                questions[i] = q
    log.info(f"questions: {len(questions)} rows")
    return questions


def load_judged(path: Path) -> dict[int, list[dict]]:
    """
    Returns: {index: [record]}
    list vì index=363 có thể dup — giữ tất cả, xử lý sau
    """
    result = defaultdict(list)
    for rec in _read_jsonl(path):
        idx = rec.get("index")
        if idx is None:
            log.warning(f"judged: record không có 'index', bỏ qua")
            continue
        result[int(idx)].append(rec)

    # Log duplicates
    dups = {k: v for k, v in result.items() if len(v) > 1}
    if dups:
        log.warning(f"judged: {len(dups)} index bị lặp — {list(dups.keys())}")

    log.info(f"judged: {len(result)} unique indices, "
             f"{sum(len(v) for v in result.values())} total records")
    return dict(result)


def load_synth(path: Path) -> dict[int, list[dict]]:
    """
    Returns: {index: [record]}
    list vì index=363 có 2 records với positive_chunk_id khác nhau
    """
    result = defaultdict(list)
    for rec in _read_jsonl(path):
        idx = rec.get("index")
        if idx is None:
            log.warning(f"synth: record không có 'index', bỏ qua")
            continue
        result[int(idx)].append(rec)

    dups = {k: v for k, v in result.items() if len(v) > 1}
    if dups:
        log.info(f"synth: {len(dups)} index bị lặp (expected: [363]) — {list(dups.keys())}")

    log.info(f"synth: {len(result)} unique indices, "
             f"{sum(len(v) for v in result.values())} total records")
    return dict(result)


def load_retrieve(path: Path) -> dict[int, dict]:
    """
    Returns: {index: record}
    Mỗi record có: query, intent, candidates (list 20, mỗi cái có chunk + bge_score + rank)
    """
    result = {}
    for rec in _read_jsonl(path):
        idx = rec.get("index")
        if idx is None:
            log.warning(f"retrieve: record không có 'index', bỏ qua")
            continue
        idx = int(idx)
        if idx in result:
            log.warning(f"retrieve: index={idx} bị lặp, giữ record đầu tiên")
            continue
        result[idx] = rec

    log.info(f"retrieve: {len(result)} records")
    return result


def load_extra_synth(path: Path, questions: dict[int, str]) -> dict[int, list[dict]]:
    """
    extra_synth không có index → map qua question text.
    questions: {index: question_text} từ load_questions()

    Returns: {index: [record, ...]}
    Mỗi record giữ nguyên fields gốc (query, positive, negative, neg_type)
    + thêm field 'index' sau khi map thành công.
    """
    # Build reverse map: question_text → index
    # Strip whitespace để tránh mismatch nhỏ
    text_to_idx = {v.strip(): k for k, v in questions.items()}

    result     = defaultdict(list)
    not_found  = 0
    total      = 0

    for rec in _read_jsonl(path):
        q = rec.get("query", "").strip()
        total += 1
        if not q:
            not_found += 1
            continue

        idx = text_to_idx.get(q)
        if idx is None:
            not_found += 1
            continue

        rec["index"] = idx
        result[idx].append(rec)

    if not_found:
        log.warning(f"extra_synth: {not_found}/{total} records không map được → "
                    f"kiểm tra lại query text có khớp Question trong question.csv không")

    log.info(f"extra_synth: {len(result)} unique indices mapped, "
             f"{sum(len(v) for v in result.values())} total records")
    return dict(result)


# ─── Build eligible set + edge cases ──────────────────────────────────────────

def build_eligible_and_edge_cases(
    judged:      dict[int, list[dict]],
    synth:       dict[int, list[dict]],
    extra_synth: dict[int, list[dict]],
    questions:   dict[int, str],
) -> tuple[set[int], dict]:
    """
    Returns:
        eligible_indices: set of indices có thể dùng cho train/eval
        edge_cases: dict mô tả các nhóm đặc biệt
    """
    gold_empty      = []  # gold_indices == []
    low_confidence  = []  # confidence == "low"
    parse_error     = []  # confidence blank hoặc record lỗi
    expanded        = []  # expanded == True, gold ngoài top-5
    synth_dup       = []  # index có > 1 synth record
    no_synth        = []  # eligible nhưng không có synth negatives
    no_extra_synth  = []  # eligible nhưng không có extra_synth negatives

    eligible = set()

    for idx, records in judged.items():
        # Lấy record đầu tiên để check (judged không dup ngoài edge case)
        rec = records[0]

        confidence  = rec.get("confidence", "")
        gold_idxs   = rec.get("gold_indices", [])
        is_expanded = rec.get("expanded", False)
        error       = rec.get("error")

        # Parse error
        if not confidence or error:
            parse_error.append(idx)
            continue

        # Low confidence → gold luôn rỗng, exclude
        if confidence == "low":
            low_confidence.append(idx)
            continue

        # Gold rỗng (medium/high confidence nhưng không tìm được gold)
        if not gold_idxs:
            gold_empty.append(idx)
            continue

        # Tới đây: có gold, confidence != low → eligible
        eligible.add(idx)

        if is_expanded:
            expanded.append(idx)

    # Synth dups
    synth_dup = [idx for idx, recs in synth.items() if len(recs) > 1]

    # Eligible nhưng không có negatives
    for idx in sorted(eligible):
        if idx not in synth or all(r.get("n_valid", 0) == 0 for r in synth[idx]):
            no_synth.append(idx)
        if idx not in extra_synth:
            no_extra_synth.append(idx)

    edge_cases = {
        "gold_empty":      sorted(gold_empty),
        "low_confidence":  sorted(low_confidence),
        "parse_error":     sorted(parse_error),
        "expanded":        sorted(expanded),
        "synth_dup":       sorted(synth_dup),
        "no_synth":        sorted(no_synth),
        "no_extra_synth":  sorted(no_extra_synth),
    }

    return eligible, edge_cases


# ─── Report ───────────────────────────────────────────────────────────────────

def print_report(
    questions:        dict,
    judged:           dict,
    synth:            dict,
    retrieve:         dict,
    extra_synth:      dict,
    eligible_indices: set,
    edge_cases:       dict,
):
    total_synth_negatives = sum(
        rec.get("n_valid", 0)
        for recs in synth.values()
        for rec in recs
    )
    total_extra = sum(len(v) for v in extra_synth.values())

    print("\n" + "=" * 55)
    print("MODULE 1 — LOAD & VALIDATE REPORT")
    print("=" * 55)
    print(f"  question.csv      : {len(questions):>5} questions")
    print(f"  judged            : {sum(len(v) for v in judged.values()):>5} records "
          f"({len(judged)} unique indices)")
    print(f"  synth             : {sum(len(v) for v in synth.values()):>5} records "
          f"→ {total_synth_negatives} valid negatives")
    print(f"  retrieve          : {len(retrieve):>5} records")
    print(f"  extra_synth       : {total_extra:>5} records "
          f"({len(extra_synth)} unique indices)")
    print()
    print(f"  ELIGIBLE indices  : {len(eligible_indices):>5}")
    print()
    print("  Edge cases:")
    for k, v in edge_cases.items():
        print(f"    {k:<20}: {len(v):>4}", end="")
        if len(v) <= 10:
            print(f"  {v}", end="")
        print()
    print("=" * 55)


# ─── Main entry point ─────────────────────────────────────────────────────────

def load_all(
    questions_path:   str | Path,
    judged_path:      str | Path,
    synth_path:       str | Path,
    retrieve_path:    str | Path,
    extra_synth_path: str | Path,
    verbose:          bool = True,
) -> dict:
    """
    Load và validate tất cả 5 file nguồn.

    Returns dict với keys:
        questions        : {index: question_text}
        judged           : {index: [record]}
        synth            : {index: [record]}
        retrieve         : {index: record}
        extra_synth      : {index: [record]}
        eligible_indices : set[int]
        edge_cases       : dict
    """
    if verbose:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%H:%M:%S",
        )

    questions   = load_questions(Path(questions_path))
    judged      = load_judged(Path(judged_path))
    synth       = load_synth(Path(synth_path))
    retrieve    = load_retrieve(Path(retrieve_path))
    # extra_synth = load_extra_synth(Path(extra_synth_path), questions)
    extra_synth = {}

    eligible_indices, edge_cases = build_eligible_and_edge_cases(
        judged, synth, extra_synth, questions
    )

    if verbose:
        print_report(questions, judged, synth, retrieve,
                     extra_synth, eligible_indices, edge_cases)

    return {
        "questions":        questions,
        "judged":           judged,
        "synth":            synth,
        "retrieve":         retrieve,
        "extra_synth":      extra_synth,
        "eligible_indices": eligible_indices,
        "edge_cases":       edge_cases,
    }


# ─── Standalone run ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions",   default=DEFAULT_QUESTIONS_PATH)
    parser.add_argument("--judged",      default=DEFAULT_JUDGED_PATH)
    parser.add_argument("--synth",       default=DEFAULT_SYNTH_PATH)
    parser.add_argument("--retrieve",    default=DEFAULT_RETRIEVE_PATH)
    parser.add_argument("--extra-synth", default=DEFAULT_EXTRA_SYNTH_PATH)
    args = parser.parse_args()

    load_all(
        questions_path   = args.questions,
        judged_path      = args.judged,
        synth_path       = args.synth,
        retrieve_path    = args.retrieve,
        extra_synth_path = args.extra_synth,
    )
