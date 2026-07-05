from __future__ import annotations


def normalize_answer(value: str | None) -> str:
    if not value:
        return ""

    labels: list[str] = []
    for ch in value.upper():
        if ch in "ABCD" and ch not in labels:
            labels.append(ch)
    return ",".join(labels)


def parse_answer(raw: str) -> tuple[int, str, bool]:
    normalized = normalize_answer(raw)
    if normalized:
        labels = normalized.split(",")
        compact = "".join(labels)
        raw_clean = raw.strip().upper().replace(",", "").replace(" ", "")
        if raw_clean == compact:
            return len(labels), normalized, True
    return 0, "X", False
