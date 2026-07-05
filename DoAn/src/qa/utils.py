from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


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
    return re.sub(r"\s+", " ", text)


def tokenize_vi(text: str) -> list[str]:
    clean = re.sub(r"[^\w\s]", " ", normalize(text))
    return [token for token in clean.split() if len(token) > 1]


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
        text = str(item.get("page_content", "")).strip()
        if not text:
            continue

        metadata = item.get("metadata", {}) if isinstance(item, dict) else {}
        chunk_id = _qualify_chunk_id(doc_scope, str(metadata.get("chunk_id") or f"chunk::{i}"))
        if chunk_id is None:
            continue

        records.append(
            ChunkRecord(
                text=text,
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
        try:
            records.extend(_load_chunk_records_from_file(chunk_file, doc_scope=chunk_file.parent.name))
        except Exception as exc:
            print(f"Warning: skip {chunk_file} ({exc})")
    return records


def detect_public_doc_ids(question: str) -> list[str]:
    matches = re.findall(r"public[_\s-]?(\d{1,3})", question, flags=re.IGNORECASE)
    doc_ids: list[str] = []
    for match in matches:
        doc_id = f"Public{int(match):03d}"
        if doc_id not in doc_ids:
            doc_ids.append(doc_id)
    return doc_ids
