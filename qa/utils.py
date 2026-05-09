from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


@dataclass
class ChunkRecord:
    text: str
    chunk_id: str
    prev_chunk_id: str | None
    next_chunk_id: str | None
    parent_id: str | None
    section_hint: str | None
    doc_scope: str
    chunk_index: int | None
    source_file: str


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize_vi(text: str) -> list[str]:
    clean = re.sub(r"[^\w\s]", " ", normalize(text))
    return [t for t in clean.split() if len(t) > 1]


def reciprocal_rank_fusion(rankings: Iterable[list[int]], k: int = 60) -> dict[int, float]:
    fused: dict[int, float] = {}
    for ranking in rankings:
        for r, idx in enumerate(ranking):
            fused[idx] = fused.get(idx, 0.0) + 1.0 / (k + r + 1)
    return fused


def top_k_indices(values: np.ndarray, k: int) -> list[int]:
    if len(values) == 0:
        return []
    k = min(k, len(values))
    if k <= 0:
        return []
    partial = np.argpartition(-values, k - 1)[:k]
    return partial[np.argsort(-values[partial])].tolist()


def _qualify_chunk_id(doc_scope: str, raw_chunk_id: str | None) -> str | None:
    if raw_chunk_id is None:
        return None
    text = str(raw_chunk_id).strip()
    if not text:
        return None
    return f"{doc_scope}::{text}"


def _load_chunk_records_from_file(chunk_file: Path, doc_scope: str) -> list[ChunkRecord]:
    with chunk_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    records: list[ChunkRecord] = []
    for i, item in enumerate(data):
        txt = str(item.get("page_content", "")).strip()
        if not txt:
            continue

        metadata = item.get("metadata", {}) if isinstance(item, dict) else {}
        raw_chunk_id = str(metadata.get("chunk_id") or f"chunk::{i}")
        chunk_id = _qualify_chunk_id(doc_scope, raw_chunk_id)
        if chunk_id is None:
            continue

        records.append(
            ChunkRecord(
                text=txt,
                chunk_id=chunk_id,
                prev_chunk_id=_qualify_chunk_id(doc_scope, metadata.get("prev_chunk_id")),
                next_chunk_id=_qualify_chunk_id(doc_scope, metadata.get("next_chunk_id")),
                parent_id=_qualify_chunk_id(doc_scope, metadata.get("parent_id")),
                section_hint=str(metadata.get("section_hint")) if metadata.get("section_hint") is not None else None,
                doc_scope=doc_scope,
                chunk_index=metadata.get("chunk_index") if isinstance(metadata.get("chunk_index"), int) else None,
                source_file=str(chunk_file),
            )
        )

    # Fallback links when prev/next are missing in metadata.
    for i, record in enumerate(records):
        if record.prev_chunk_id is None and i > 0:
            record.prev_chunk_id = records[i - 1].chunk_id
        if record.next_chunk_id is None and i + 1 < len(records):
            record.next_chunk_id = records[i + 1].chunk_id

    return records


def load_all_chunks(chunk_dir: Path) -> list[ChunkRecord]:
    records: list[ChunkRecord] = []
    chunk_files = sorted(chunk_dir.glob("*/*_chunks*.json"))
    if not chunk_files:
        chunk_files = sorted(chunk_dir.glob("*/*.json"))
    for chunk_file in chunk_files:
        doc_scope = chunk_file.parent.name
        try:
            records.extend(_load_chunk_records_from_file(chunk_file, doc_scope=doc_scope))
        except Exception as e:
            print(f"Warning: skip {chunk_file} ({e})")
    return records


def load_doc_chunks(chunk_dir: Path, doc_id: str) -> list[ChunkRecord]:
    doc_dir = chunk_dir / doc_id
    # Tìm file *_chunks.json bất kỳ trong thư mục doc (hỗ trợ các tên khác nhau)
    chunk_files = sorted(doc_dir.glob("*_chunks*.json"))
    if not chunk_files:
        # Fallback: tìm bất kỳ .json nào
        chunk_files = sorted(doc_dir.glob("*.json"))
    if not chunk_files:
        return []

    chunk_file = chunk_files[0]  # Lấy file đầu tiên
    try:
        return _load_chunk_records_from_file(chunk_file, doc_scope=doc_id)
    except Exception as e:
        print(f"Warning: skip {chunk_file} ({e})")
        return []


def load_all_chunk_texts(chunk_dir: Path) -> list[str]:
    return [c.text for c in load_all_chunks(chunk_dir)]


def load_doc_chunk_texts(chunk_dir: Path, doc_id: str) -> list[str]:
    return [c.text for c in load_doc_chunks(chunk_dir, doc_id)]


def detect_public_doc_ids(question: str) -> list[str]:
    matches = re.findall(r"public[_\s-]?(\d{1,3})", question, flags=re.IGNORECASE)
    doc_ids: list[str] = []
    for m in matches:
        doc_id = f"Public{int(m):03d}"
        if doc_id not in doc_ids:
            doc_ids.append(doc_id)
    return doc_ids


def stable_texts_fingerprint(texts: list[str]) -> str:
    hasher = hashlib.sha256()
    for text in texts:
        hasher.update(text.encode("utf-8", errors="ignore"))
        hasher.update(b"\0")
    return hasher.hexdigest()


def sanitize_for_filename(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]", "_", name)


def _parse_answer_tokens(text: str) -> list[str]:
    candidate = text.strip().upper()
    candidate = candidate.strip('"\'` .:;，。、)］]}>-–—')
    candidate = re.sub(r"\s+", "", candidate)

    if candidate == "?":
        return []

    if not re.fullmatch(r"[ABCD](?:,[ABCD]){0,3}", candidate):
        return []

    return candidate.split(",")


def parse_answer_text(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    # Priority 1: Check for explicit ANSWER: / ĐÁP ÁN: / etc. anywhere, scanning from bottom up
    for line in reversed(lines):
        match = re.search(r'(?:ANSWER|ANS|ĐÁP ÁN(?: LÀ)?|KẾT QUẢ(?: LÀ)?)\s*:?\s*\*?\*?\s*([A-D](?:\s*,\s*[A-D])*)\b', line, re.IGNORECASE)
        if match:
            return [c.strip().upper() for c in match.group(1).split(',')]
            
    # Priority 2: Check for A. text... at the beginning
    for line in lines:
        match = re.match(r'^([A-D])\.', line, re.IGNORECASE)
        if match:
            return [match.group(1).upper()]
            
    # Priority 3: Fallback finding isolated letters at the very end
    if lines:
        last_line = lines[-1]
        match = re.search(r'\b([A-D](?:\s*,\s*[A-D])*)\b', last_line, re.IGNORECASE)
        if match and len(match.group(1).split(',')) <= 4:
            if re.fullmatch(r'([A-D](?:\s*,\s*[A-D])*)', match.group(1).upper().replace(' ', '')):
                return [c.strip().upper() for c in match.group(1).split(',')]

    if len(lines) == 1:
        parsed = _parse_answer_tokens(lines[0])
        if parsed:
            return parsed

    return []

def parse_result_line(line: str) -> tuple[int | None, list[str], str]:
    raw = line.strip()
    if not raw:
        return None, [], raw

    parts = raw.split(",", 1)
    if len(parts) != 2:
        return None, [], raw

    try:
        num_corrects = int(parts[0].strip())
    except Exception:
        return None, [], raw

    answer_part = parts[1].strip().strip('"').strip()
    if answer_part == "?" or answer_part == "":
        return num_corrects, [], raw

    labels = [x.strip().upper() for x in answer_part.split(",") if x.strip()]
    labels = sorted(set([x for x in labels if x in {"A", "B", "C", "D"}]))
    return num_corrects, labels, raw


def save_mismatch_questions(results: list[str], truth_file: Path, mismatch_output: Path) -> int:
    if not truth_file.exists():
        print(f"Warning: truth file not found: {truth_file}")
        return 0

    truth_lines = [line.strip() for line in truth_file.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
    pred_lines = [line.strip() for line in results if line.strip()]

    n = min(len(pred_lines), len(truth_lines))
    mismatches: list[dict[str, str]] = []

    for i in range(n):
        p_num, p_labels, p_raw = parse_result_line(pred_lines[i])
        t_num, t_labels, t_raw = parse_result_line(truth_lines[i])

        is_diff = False
        if p_num is None or t_num is None:
            is_diff = p_raw != t_raw
        else:
            is_diff = (p_num != t_num) or (p_labels != t_labels)

        if is_diff:
            mismatches.append({"question": str(i + 1), "pred": p_raw, "truth": t_raw})

    if len(pred_lines) != len(truth_lines):
        print(
            "Warning: pred/truth line counts differ. "
            f"Comparing overlapped range only ({n} lines)."
        )

    mismatch_output.parent.mkdir(parents=True, exist_ok=True)
    with mismatch_output.open("w", encoding="utf-8") as f:
        f.write("# Mismatch Questions\n\n")
        f.write(f"- Compared (overlapped): {n}\n")
        f.write(f"- Pred lines: {len(pred_lines)}\n")
        f.write(f"- Truth lines: {len(truth_lines)}\n")
        f.write(f"- Total mismatches: {len(mismatches)}\n\n")
        f.write("| Question | Predicted | Truth |\n")
        f.write("|---|---|---|\n")
        for item in mismatches:
            pred = item["pred"].replace("|", "\\|")
            truth = item["truth"].replace("|", "\\|")
            f.write(f"| {item['question']} | {pred} | {truth} |\n")

    return len(mismatches)
