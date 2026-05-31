from __future__ import annotations

import csv
from pathlib import Path

from qa.answer_utils import normalize_answer


def load_questions(path: Path) -> list[dict]:
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
