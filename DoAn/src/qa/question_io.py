from __future__ import annotations

import csv
import json
from pathlib import Path

from qa.answer_utils import normalize_answer


def _normalize_options(raw_options) -> list[str]:
    if isinstance(raw_options, dict):
        return [str(raw_options.get(letter, "") or "").strip() for letter in ["A", "B", "C", "D"]]
    if isinstance(raw_options, list):
        options = [str(value or "").strip() for value in raw_options[:4]]
        return options + [""] * (4 - len(options))
    return ["", "", "", ""]


def _load_json_questions(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON list in {path}")

    questions: list[dict] = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            continue

        question = str(item.get("question") or item.get("Question") or "").strip()
        if not question:
            continue

        truth = item.get("answer") or item.get("Answer") or item.get("truth") or item.get("Truth")
        q_item = {
            "index": idx,
            "question": question,
            "options": _normalize_options(item.get("options")),
            "ground_truth": normalize_answer(str(truth or "")) or None,
        }
        if "gold_chunk_ids" in item:
            q_item["gold_chunk_ids"] = item["gold_chunk_ids"]
        if "difficulty" in item:
            q_item["difficulty"] = item["difficulty"]
        questions.append(q_item)

    print(f"Loaded {len(questions)} questions from {path}")
    return questions


def load_questions(path: Path) -> list[dict]:
    if path.suffix.lower() == ".json":
        return _load_json_questions(path)

    questions: list[dict] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if "Question" not in (reader.fieldnames or []):
            raise ValueError(f"Missing Question column in {path}")

        for idx, row in enumerate(reader):
            question = row.get("Question", "").strip()
            if not question:
                continue

            truth = row.get("Truth", "").strip() or row.get("Answer", "").strip()
            questions.append({
                "index": idx,
                "question": question,
                "options": [
                    row.get("A", "").strip(),
                    row.get("B", "").strip(),
                    row.get("C", "").strip(),
                    row.get("D", "").strip(),
                ],
                "ground_truth": normalize_answer(truth) or None,
            })

    print(f"Loaded {len(questions)} questions from {path}")
    return questions


def load_router_questions(path: Path) -> list[dict]:
    questions: list[dict] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if "Question" not in (reader.fieldnames or []):
            raise ValueError(f"Missing Question column in {path}")

        for row in reader:
            question = row.get("Question", "").strip()
            if not question:
                continue

            options = {}
            for letter in ["A", "B", "C", "D"]:
                value = row.get(letter, "").strip()
                if value:
                    options[letter] = value

            truth = row.get("Truth", "").strip() or row.get("Answer", "").strip()
            questions.append({
                "question": question,
                "options": options if options else None,
                "truth": normalize_answer(truth) or None,
            })

    print(f"Loaded {len(questions)} questions from {path}")
    return questions
