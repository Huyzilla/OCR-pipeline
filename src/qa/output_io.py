from __future__ import annotations

import csv
import json
from pathlib import Path


def load_json_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def save_json_list(path: Path, data: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_done_indices(path: Path) -> set[int]:
    if not path.exists():
        return set()

    done: set[int] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                done.add(int(row["question_index"]))
            except Exception:
                continue
    return done


def trim_output_csv(path: Path, keep_indices: set[int]) -> None:
    if not path.exists():
        return

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = []
        for row in reader:
            try:
                if int(row["question_index"]) in keep_indices:
                    rows.append(row)
            except Exception:
                continue

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if fieldnames:
            writer.writeheader()
            writer.writerows(rows)


def trim_debug_log(path: Path, keep_indices: set[int]) -> list[dict]:
    rows = []
    for item in load_json_list(path):
        try:
            question_index = int(item.get("question_index", item.get("id", -1) + 1))
        except Exception:
            continue
        if question_index in keep_indices:
            rows.append(item)
    save_json_list(path, rows)
    return rows
