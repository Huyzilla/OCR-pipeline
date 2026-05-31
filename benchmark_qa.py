#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmark QA outputs and reranker latency in one place.

Default command:
    python benchmark_qa.py

Reranker benchmark:
    python benchmark_qa.py --mode reranker --new-reranker reranker_stage2/best
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from collections import defaultdict
from pathlib import Path


BENCHMARK_MODE = "answers"  # answers | reranker

DATA_DIR = Path("data")
QUESTION_CSV = DATA_DIR / "question.csv"
INTENT_CSV = DATA_DIR / "qwen_intent_classification.csv"

BASELINE_CSV = Path("baseline.csv")
BASELINE_JSON = Path("baseline_debug.json")
FUSION_CSV = Path("fusion.csv")
FUSION_JSON = Path("fusion_debug.json")
ROUTER_CSV = Path("router.csv")
ROUTER_JSON = None

OUTPUT_JSON = None

NEW_RERANKER = None
RERANKER_BASELINE_JSON = BASELINE_JSON
RERANKER_OUTPUT_DIR = Path("benchmark_reranker")


def parse_answer_line(line: str) -> tuple[int, tuple[str, ...]]:
    raw = line.strip()
    if not raw:
        return 0, ()
    parts = raw.split(",", 1)
    if len(parts) != 2:
        return 0, ()
    try:
        num = int(parts[0].strip())
    except ValueError:
        return 0, ()

    ans = parts[1].strip().strip('"').strip()
    labels = tuple(sorted(
        set(x.strip().upper() for x in ans.split(",") if x.strip().upper() in "ABCD")
    ))
    return num, labels


def labels_from_text(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    labels = []
    for ch in value.upper():
        if ch in "ABCD" and ch not in labels:
            labels.append(ch)
    return tuple(sorted(labels))


def load_answers_csv(path: Path) -> list[tuple[int, tuple[str, ...]]]:
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        has_header = "predicted" in sample.splitlines()[0].lower() if sample.splitlines() else False

        if has_header:
            reader = csv.DictReader(f)
            for row in reader:
                labels = labels_from_text(row.get("predicted"))
                rows.append((len(labels), labels))
        else:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    rows.append(parse_answer_line(",".join(row)))
    return rows


def load_truth_from_questions(path: Path) -> list[tuple[int, tuple[str, ...]]]:
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        answer_col = "Answer" if "Answer" in fields else "Truth" if "Truth" in fields else None
        if not answer_col:
            raise ValueError(f"Missing Answer column in {path}")
        for row in reader:
            labels = labels_from_text(row.get(answer_col))
            rows.append((len(labels), labels))
    return rows


def load_intent_csv(path: Path) -> dict[int, str]:
    result = {}
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            result[int(row["question_index"])] = row["intent"].strip()
    return result


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_router_json(path: Path) -> dict[int, dict]:
    data = load_json(path)
    return {int(e["index"]): e for e in data}


def debug_map_from_log(debug_log: list[dict] | None) -> dict[int, dict]:
    result = {}
    if not debug_log:
        return result
    for entry in debug_log:
        if "question_index" in entry:
            idx = int(entry["question_index"])
        else:
            idx = int(entry.get("id", 0)) + 1
        result[idx] = entry
    return result


def get_debug_latency(entry: dict) -> float | None:
    perf = entry.get("performance", {})
    if "latency_s" in perf:
        return perf["latency_s"]
    if "total_ms" in perf:
        return perf["total_ms"] / 1000
    timing = entry.get("timing", {})
    if {"retrieve_s", "rerank_s", "llm_s"} <= set(timing):
        return timing["retrieve_s"] + timing["rerank_s"] + timing["llm_s"]
    return None


def get_debug_format_ok(entry: dict) -> bool:
    if "generation" in entry:
        return bool(entry.get("generation", {}).get("format_ok", True))
    return bool(entry.get("format_ok", True))


def get_debug_raw(entry: dict) -> str:
    if "generation" in entry:
        return entry.get("generation", {}).get("raw", "")
    return entry.get("llm_raw_output") or entry.get("raw_answer", "")


def get_debug_doc_ids(entry: dict) -> list[str]:
    retrieval = entry.get("retrieval", {})
    if "doc_ids" in retrieval:
        return retrieval.get("doc_ids", [])
    chunk_ids = [c.get("chunk_id", "") for c in entry.get("retrieved_chunks", [])]
    return list(dict.fromkeys(cid.split("::")[0] for cid in chunk_ids if cid))


def evaluate_answers(
    name: str,
    pred: list[tuple[int, tuple[str, ...]]],
    truth: list[tuple[int, tuple[str, ...]]],
    gt_intents: dict[int, str],
    debug_log: list[dict] | None = None,
    router_json: dict[int, dict] | None = None,
) -> dict:
    n = min(len(pred), len(truth))
    debug_map = debug_map_from_log(debug_log)

    records = []
    for i in range(n):
        idx = i + 1
        p_num, p_lab = pred[i]
        t_num, t_lab = truth[i]
        debug_entry = debug_map.get(idx, {})
        router_entry = router_json.get(idx) if router_json else None
        gt_intent = gt_intents.get(idx, "unknown")

        records.append({
            "index": idx,
            "question": (debug_entry.get("question") or (router_entry or {}).get("question", ""))[:120],
            "truth": (t_num, t_lab),
            "pred": (p_num, p_lab),
            "is_correct": p_num == t_num and p_lab == t_lab,
            "gt_intent": gt_intent,
            "ro_intent": (router_entry or {}).get("intent"),
            "retrieve_mode": (router_entry or {}).get("retrieve_mode") or debug_entry.get("retrieve_mode"),
            "latency": get_debug_latency(debug_entry),
            "format_ok": get_debug_format_ok(debug_entry),
            "raw_answer": get_debug_raw(debug_entry),
            "doc_ids": get_debug_doc_ids(debug_entry),
        })

    total = len(records)
    correct = sum(1 for r in records if r["is_correct"])

    by_intent = defaultdict(lambda: {"total": 0, "correct": 0})
    for r in records:
        by_intent[r["gt_intent"]]["total"] += 1
        by_intent[r["gt_intent"]]["correct"] += int(r["is_correct"])

    intent_accuracy = {
        intent: {
            "correct": v["correct"],
            "total": v["total"],
            "accuracy": round(v["correct"] / v["total"], 4) if v["total"] else 0,
        }
        for intent, v in sorted(by_intent.items())
    }

    multi = [r for r in records if r["truth"][0] > 1]
    multi_correct = sum(1 for r in multi if r["is_correct"])

    latencies = [r["latency"] for r in records if r["latency"] is not None]
    latency = {}
    if latencies:
        filtered = [x for x in latencies if x <= 60]
        use = filtered or latencies
        latency = {
            "mean_s": round(sum(use) / len(use), 2),
            "min_s": round(min(use), 2),
            "max_s": round(max(use), 2),
            "total_min": round(sum(use) / 60, 1),
            "n_measured": len(use),
            "outliers_removed": len(latencies) - len(use),
        }

    format_errors = [
        {
            "index": r["index"],
            "gt_intent": r["gt_intent"],
            "truth": answer_to_text(r["truth"]),
            "raw_answer": r["raw_answer"],
        }
        for r in records if not r["format_ok"]
    ]

    by_mode = defaultdict(lambda: {"total": 0, "correct": 0})
    for r in records:
        if r["retrieve_mode"]:
            by_mode[r["retrieve_mode"]]["total"] += 1
            by_mode[r["retrieve_mode"]]["correct"] += int(r["is_correct"])
    retrieve_mode = {
        mode: {
            "count": v["total"],
            "correct": v["correct"],
            "accuracy": round(v["correct"] / v["total"], 4) if v["total"] else 0,
        }
        for mode, v in sorted(by_mode.items())
    }

    intent_clf = None
    clf_records = [r for r in records if r["ro_intent"] is not None]
    if clf_records:
        clf_correct = sum(1 for r in clf_records if r["ro_intent"] == r["gt_intent"])
        intent_clf = {
            "correct": clf_correct,
            "total": len(clf_records),
            "accuracy": round(clf_correct / len(clf_records), 4),
            "mismatch": [
                {
                    "index": r["index"],
                    "question": r["question"],
                    "gt_intent": r["gt_intent"],
                    "ro_intent": r["ro_intent"],
                    "truth": answer_to_text(r["truth"]),
                    "pred": answer_to_text(r["pred"]),
                    "is_correct": r["is_correct"],
                }
                for r in clf_records if r["ro_intent"] != r["gt_intent"]
            ],
        }

    wrong = [
        {
            "index": r["index"],
            "question": r["question"],
            "gt_intent": r["gt_intent"],
            "truth": answer_to_text(r["truth"]),
            "pred": answer_to_text(r["pred"]),
            "format_ok": r["format_ok"],
            "retrieve_mode": r["retrieve_mode"],
            "doc_ids": r["doc_ids"],
        }
        for r in records if not r["is_correct"]
    ]

    return {
        "pipeline": name,
        "total": total,
        "correct": correct,
        "accuracy": round(correct / total, 4) if total else 0,
        "intent_accuracy": intent_accuracy,
        "multi_answer": {
            "total": len(multi),
            "correct": multi_correct,
            "accuracy": round(multi_correct / len(multi), 4) if multi else 0,
        },
        "latency": latency,
        "format_errors": format_errors,
        "retrieve_mode": retrieve_mode,
        "intent_classification": intent_clf,
        "wrong_answers": wrong,
    }


def answer_to_text(answer: tuple[int, tuple[str, ...]]) -> str:
    return f"{answer[0]},{','.join(answer[1]) if answer[1] else 'X'}"


def bar(ratio: float, width: int = 30) -> str:
    n = round(ratio * width)
    return "#" * n + "." * (width - n)


def print_answer_report(result: dict) -> None:
    print("\n" + "=" * 70)
    print(f"{result['pipeline'].upper()} BENCHMARK")
    print("=" * 70)
    acc = result["accuracy"]
    print(f"Overall [{bar(acc)}] {result['correct']}/{result['total']} ({acc:.2%})")

    print("\nAccuracy by intent")
    for intent, v in result["intent_accuracy"].items():
        print(f"  {intent:<14} {v['correct']:>4}/{v['total']:<4} ({v['accuracy']:.2%})")

    ma = result["multi_answer"]
    if ma["total"]:
        print(f"\nMulti-answer: {ma['correct']}/{ma['total']} ({ma['accuracy']:.2%})")

    if result["latency"]:
        lat = result["latency"]
        print(
            f"\nLatency: mean={lat['mean_s']}s min={lat['min_s']}s "
            f"max={lat['max_s']}s total={lat['total_min']}min"
        )

    if result["retrieve_mode"]:
        print("\nAccuracy by retrieve mode")
        for mode, v in result["retrieve_mode"].items():
            print(f"  {mode:<16} {v['correct']:>4}/{v['count']:<4} ({v['accuracy']:.2%})")

    clf = result.get("intent_classification")
    if clf:
        print(f"\nRouter intent: {clf['correct']}/{clf['total']} ({clf['accuracy']:.2%})")
        if clf["mismatch"]:
            print(f"  Mismatch: {len(clf['mismatch'])}")

    if result["format_errors"]:
        print(f"\nFormat errors: {len(result['format_errors'])}")

    wrong = result["wrong_answers"]
    print(f"\nWrong answers: {len(wrong)}")
    for item in wrong[:20]:
        mode = f"[{item['retrieve_mode']}]" if item["retrieve_mode"] else ""
        print(
            f"  Q{item['index']:>4} {item['gt_intent']:<12} {mode:<18} "
            f"pred={item['pred']:<8} truth={item['truth']:<8} {item['question'][:50]}"
        )


def print_comparison(results: list[dict]) -> None:
    if len(results) < 2:
        return
    print("\n" + "=" * 70)
    print("SUMMARY COMPARISON")
    print("=" * 70)
    for r in results:
        ferr = len(r["format_errors"])
        lat = f"{r['latency']['mean_s']}s" if r["latency"] else "N/A"
        print(
            f"{r['pipeline']:<14} {r['correct']:>4}/{r['total']:<4} "
            f"({r['accuracy']:.2%})  format_err={ferr:<4} latency={lat}"
        )


def build_answer_jobs(args) -> list[tuple[str, Path, Path | None]]:
    jobs = []
    if args.pred_csv:
        jobs.append((args.name, args.pred_csv, args.debug_json))
        return jobs

    for name, csv_path, json_path in [
        ("Baseline", args.baseline_csv, args.baseline_json),
        ("Fusion", args.fusion_csv, args.fusion_json),
        ("Router", args.router_csv, None),
    ]:
        if csv_path and csv_path.exists():
            jobs.append((name, csv_path, json_path if json_path and json_path.exists() else None))
    return jobs


def run_answer_benchmark(args) -> int:
    if args.dry_run:
        print("Answer benchmark configuration")
        print(f"  question_csv : {args.question_csv}")
        print(f"  intent_csv   : {args.intent_csv}")
        print(f"  pred_csv     : {args.pred_csv}")
        print(f"  baseline_csv : {args.baseline_csv}")
        print(f"  fusion_csv   : {args.fusion_csv}")
        print(f"  router_csv   : {args.router_csv}")
        print(f"  router_json  : {args.router_json}")
        return 0

    for path in [args.question_csv, args.intent_csv]:
        if not path.exists():
            print(f"Missing required file: {path}")
            return 1

    jobs = build_answer_jobs(args)
    if not jobs:
        print("No prediction CSV found. Pass --pred-csv or create baseline/fusion/router CSV files.")
        return 1

    truth = load_truth_from_questions(args.question_csv)
    gt_intents = load_intent_csv(args.intent_csv)
    router_json = None
    if args.router_json and args.router_json.exists():
        router_json = load_router_json(args.router_json)

    results = []
    for name, csv_path, json_path in jobs:
        print(f"\nLoading {name}: {csv_path}")
        pred = load_answers_csv(csv_path)
        debug_log = load_json(json_path) if json_path else None
        if len(pred) != len(truth):
            print(f"  Count mismatch: pred={len(pred)}, truth={len(truth)}")
        result = evaluate_answers(name, pred, truth, gt_intents, debug_log, router_json)
        print_answer_report(result)
        results.append(result)

    print_comparison(results)

    if args.output_json:
        payload = results[0] if len(results) == 1 else results
        with args.output_json.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"Saved -> {args.output_json}")

    return 0


def load_reranker(model_path: str):
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    import torch

    print(f"Loading reranker: {model_path}")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path, num_labels=1)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    print(f"  Device: {device}")
    return tokenizer, model, device


def score_passages(tokenizer, model, device, query: str, passages: list[str]) -> list[float]:
    import torch

    if not passages:
        return []
    enc = tokenizer(
        [query] * len(passages),
        passages,
        max_length=256,
        padding=True,
        truncation=True,
        return_tensors="pt",
    )
    enc = {k: v.to(device) for k, v in enc.items()}
    with torch.no_grad():
        scores = model(**enc).logits.squeeze(-1)
    return scores.cpu().tolist()


def passages_from_debug(entry: dict) -> tuple[list[str], list[str]]:
    retrieval = entry.get("retrieval", {})
    top_chunks = retrieval.get("top_chunks", [])
    if top_chunks:
        passages = [c.get("text", "") for c in top_chunks if c.get("text")]
        chunk_ids = [c.get("chunk_id", "") for c in top_chunks if c.get("text")]
        return passages, chunk_ids

    context = retrieval.get("recall_check_text", "")
    chunk_ids = retrieval.get("chunk_ids", [])
    if not context or not chunk_ids:
        return [], []

    raw_parts = context.split("\n\n")
    if len(raw_parts) < len(chunk_ids):
        return raw_parts, chunk_ids[:len(raw_parts)]

    group_size = max(1, len(raw_parts) // len(chunk_ids))
    passages = []
    for i in range(len(chunk_ids)):
        start = i * group_size
        end = start + group_size if i < len(chunk_ids) - 1 else len(raw_parts)
        passages.append("\n\n".join(raw_parts[start:end]))
    return passages, chunk_ids


def baseline_answer_accuracy(baseline_log: list[dict], truth: list[tuple[int, tuple[str, ...]]], gt_intents: dict[int, str]) -> dict:
    total, correct = 0, 0
    by_intent = defaultdict(lambda: {"total": 0, "correct": 0})
    for entry in baseline_log:
        idx = int(entry.get("question_index", entry.get("id", 0) + 1))
        if idx > len(truth):
            continue
        pred_labels = labels_from_text(entry.get("predicted"))
        pred = (len(pred_labels), pred_labels)
        is_correct = pred == truth[idx - 1]
        intent = gt_intents.get(idx, "unknown")
        total += 1
        correct += int(is_correct)
        by_intent[intent]["total"] += 1
        by_intent[intent]["correct"] += int(is_correct)

    return {
        "total": total,
        "correct": correct,
        "accuracy": round(correct / total, 4) if total else 0,
        "by_intent": {
            intent: {
                "correct": v["correct"],
                "total": v["total"],
                "accuracy": round(v["correct"] / v["total"], 4) if v["total"] else 0,
            }
            for intent, v in sorted(by_intent.items())
        },
    }


def run_reranker_benchmark(args) -> int:
    if not args.new_reranker:
        print("Missing --new-reranker for reranker benchmark.")
        return 1
    if args.dry_run:
        print("Reranker benchmark configuration")
        print(f"  new_reranker : {args.new_reranker}")
        print(f"  baseline_json: {args.baseline_json}")
        print(f"  question_csv : {args.question_csv}")
        print(f"  intent_csv   : {args.intent_csv}")
        print(f"  output_dir   : {args.output_dir}")
        return 0

    for path in [args.baseline_json, args.question_csv, args.intent_csv]:
        if not path.exists():
            print(f"Missing required file: {path}")
            return 1

    baseline_log = load_json(args.baseline_json)
    truth = load_truth_from_questions(args.question_csv)
    gt_intents = load_intent_csv(args.intent_csv)

    baseline_acc = baseline_answer_accuracy(baseline_log, truth, gt_intents)
    print("\nBaseline answer accuracy")
    print(f"  {baseline_acc['correct']}/{baseline_acc['total']} ({baseline_acc['accuracy']:.2%})")
    for intent, v in baseline_acc["by_intent"].items():
        print(f"  {intent}: {v['correct']}/{v['total']} ({v['accuracy']:.2%})")

    tokenizer, model, device = load_reranker(args.new_reranker)
    latencies = []
    results = []

    for entry in baseline_log:
        idx = int(entry.get("question_index", entry.get("id", 0) + 1))
        passages, chunk_ids = passages_from_debug(entry)
        if not passages:
            results.append({"idx": idx, "reranked": False})
            continue

        t0 = time.perf_counter()
        scores = score_passages(tokenizer, model, device, entry["question"], passages)
        latency_ms = (time.perf_counter() - t0) * 1000
        latencies.append(latency_ms)

        ranked_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        results.append({
            "idx": idx,
            "intent": gt_intents.get(idx, "unknown"),
            "reranked": True,
            "top1_chunk": chunk_ids[ranked_idx[0]] if ranked_idx else None,
            "ranked_ids": [chunk_ids[i] for i in ranked_idx],
            "latency_ms": round(latency_ms, 2),
        })

    latency = {}
    if latencies:
        import numpy as np

        lat = np.array(latencies)
        latency = {
            "mean_ms": round(float(lat.mean()), 2),
            "p50_ms": round(float(np.percentile(lat, 50)), 2),
            "p95_ms": round(float(np.percentile(lat, 95)), 2),
            "total_min": round(float(lat.sum()) / 60000, 1),
        }

    print("\nReranker latency")
    print(
        f"  mean={latency.get('mean_ms')}ms "
        f"p50={latency.get('p50_ms')}ms "
        f"p95={latency.get('p95_ms')}ms "
        f"total={latency.get('total_min')}min"
    )
    print("  Note: this measures reranker inference only, not full LLM QA accuracy.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = {
        "baseline_accuracy": baseline_acc,
        "new_reranker_eval": {
            "model": args.new_reranker,
            "n_results": len(results),
            "latency": latency,
        },
    }
    out_path = args.output_dir / "reranker_benchmark.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Saved -> {out_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark QA predictions or reranker latency.")
    parser.add_argument("--mode", choices=["answers", "reranker"], default=BENCHMARK_MODE)
    parser.add_argument("--question-csv", type=Path, default=QUESTION_CSV)
    parser.add_argument("--intent-csv", type=Path, default=INTENT_CSV)
    parser.add_argument("--output-json", type=Path, default=OUTPUT_JSON)
    parser.add_argument("--dry-run", action="store_true")

    parser.add_argument("--pred-csv", type=Path, default=None)
    parser.add_argument("--name", default="Prediction")
    parser.add_argument("--debug-json", type=Path, default=None)
    parser.add_argument("--baseline-csv", type=Path, default=BASELINE_CSV)
    parser.add_argument("--baseline-json", type=Path, default=BASELINE_JSON)
    parser.add_argument("--fusion-csv", type=Path, default=FUSION_CSV)
    parser.add_argument("--fusion-json", type=Path, default=FUSION_JSON)
    parser.add_argument("--router-csv", type=Path, default=ROUTER_CSV)
    parser.add_argument("--router-json", type=Path, default=ROUTER_JSON)

    parser.add_argument("--new-reranker", default=NEW_RERANKER)
    parser.add_argument("--output-dir", type=Path, default=RERANKER_OUTPUT_DIR)
    args = parser.parse_args()

    if args.new_reranker and args.mode == "answers":
        args.mode = "reranker"

    if args.mode == "reranker":
        return run_reranker_benchmark(args)
    return run_answer_benchmark(args)


if __name__ == "__main__":
    raise SystemExit(main())
