from __future__ import annotations

import argparse
import csv
from pathlib import Path


TRUE_VALUES = {"1", "true", "yes", "y", "correct"}


def parse_bool(value: str | None) -> bool:
    return (value or "").strip().lower() in TRUE_VALUES


def parse_float(value: str | None, *, column: str, row_number: int) -> float:
    text = (value or "").strip()
    if not text:
        return 0.0
    try:
        return float(text)
    except ValueError as exc:
        raise ValueError(
            f"Cannot parse numeric value in column '{column}' at row {row_number}: {text!r}"
        ) from exc


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError(f"No result rows found in {path}")

    required = {"is_correct", "rerank_ms"}
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"Missing required columns in {path}: {sorted(missing)}")

    return rows


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize benchmark result CSV metrics."
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        type=Path,
        default=Path("baseline_test_questions.csv"),
        help="Result CSV path. Default: baseline_test_questions.csv",
    )
    parser.add_argument(
        "--wall-time-seconds",
        type=float,
        default=None,
        help=(
            "Use this wall-clock time instead of summing total_ms. "
            "Useful when you want to reproduce the exact elapsed time printed by the run log."
        ),
    )
    args = parser.parse_args()

    rows = load_rows(args.csv_path)
    total = len(rows)
    correct = sum(parse_bool(row.get("is_correct")) for row in rows)
    avg_rerank_ms = (
        sum(
            parse_float(row.get("rerank_ms"), column="rerank_ms", row_number=i)
            for i, row in enumerate(rows, start=2)
        )
        / total
    )

    if args.wall_time_seconds is not None:
        wall_time_s = args.wall_time_seconds
    elif "total_ms" in rows[0]:
        wall_time_s = sum(
            parse_float(row.get("total_ms"), column="total_ms", row_number=i)
            for i, row in enumerate(rows, start=2)
        ) / 1000.0
    else:
        wall_time_s = None

    print(f"Questions run:     {total}")
    print(f"Correct:           {correct}/{total} ({correct / total * 100:.1f}%)")
    print(f"Avg rerank:        {avg_rerank_ms:.1f} ms/question")
    if wall_time_s is None:
        print("Total wall time:   N/A")
    else:
        print(f"Total wall time:   {wall_time_s:.1f}s ({wall_time_s / 60:.1f} min)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
