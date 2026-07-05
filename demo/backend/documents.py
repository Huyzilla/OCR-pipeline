from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .paths import CORPUS_CHUNK_DIR, CORPUS_OCR_DIR, UPLOAD_CHUNK_DIR, UPLOAD_DIR, UPLOAD_OCR_DIR, ensure_runtime_dirs, setup_project_paths

setup_project_paths()


def list_ocr_documents(ocr_dir: Path = CORPUS_OCR_DIR) -> list[str]:
    if not ocr_dir.exists():
        return []
    return sorted(
        item.name
        for item in ocr_dir.iterdir()
        if item.is_dir() and (item / "main.md").exists()
    )


def candidate_doc_ids(pdf_name: str) -> list[str]:
    stem = Path(pdf_name).stem.strip()
    compact = re.sub(r"[\s_-]+", "", stem)
    variants = [stem, stem.replace(" ", "_")]

    match = re.match(r"(?i)^public(\d+)$", compact)
    if match:
        number = int(match.group(1))
        variants.extend([f"Public_{number}", f"Public_{number:03d}", f"Public{number:03d}"])

    seen = []
    for value in variants:
        if value and value not in seen:
            seen.append(value)
    return seen


def find_existing_ocr(pdf_name: str, corpus_ocr_dir: Path = CORPUS_OCR_DIR) -> tuple[str, Path] | None:
    for doc_id in candidate_doc_ids(pdf_name):
        md_path = corpus_ocr_dir / doc_id / "main.md"
        if md_path.exists():
            return doc_id, md_path
    return None


def save_uploaded_pdf(file_name: str, data: bytes) -> Path:
    ensure_runtime_dirs()
    target = UPLOAD_DIR / Path(file_name).name
    target.write_bytes(data)
    return target


def ensure_chunk_for_markdown(md_path: Path, output_chunk_dir: Path, doc_id: str) -> Path:
    from rag.main_chunking import load_config, process_one_file

    output_json = output_chunk_dir / doc_id / "main_chunks_viettel.json"
    if output_json.exists() and output_json.stat().st_mtime >= md_path.stat().st_mtime:
        return output_json

    config = load_config(None)
    process_one_file(md_path, output_json, config, doc_id=doc_id)
    return output_json


def prepare_existing_document(
    doc_id: str,
    md_path: Path,
    corpus_chunk_dir: Path = CORPUS_CHUNK_DIR,
) -> dict[str, Any]:
    chunk_json = corpus_chunk_dir / doc_id / "main_chunks_viettel.json"
    chunk_dir = corpus_chunk_dir

    if not chunk_json.exists():
        chunk_json = ensure_chunk_for_markdown(md_path, UPLOAD_CHUNK_DIR, doc_id)
        chunk_dir = UPLOAD_CHUNK_DIR

    return {
        "doc_id": doc_id,
        "md_path": md_path,
        "chunk_dir": chunk_dir,
        "chunk_json": chunk_json,
        "ocr_elapsed": 0.0,
        "source": "existing",
    }


def run_uploaded_pdf_ocr(uploaded_pdf: Path, table_format: str = "html") -> dict[str, Any]:
    from ocr.ocr import extract_pdf_folder_name
    from run_ocr import process_single_pdf

    ensure_runtime_dirs()
    elapsed = process_single_pdf(
        input_pdf=uploaded_pdf,
        output_dir=UPLOAD_OCR_DIR,
        html_tables=(table_format == "html"),
    )
    doc_id = extract_pdf_folder_name(uploaded_pdf)
    md_path = UPLOAD_OCR_DIR / doc_id / "main.md"
    if not md_path.exists():
        raise FileNotFoundError(f"OCR đã chạy nhưng không tìm thấy {md_path}")

    chunk_json = ensure_chunk_for_markdown(md_path, UPLOAD_CHUNK_DIR, doc_id)
    return {
        "doc_id": doc_id,
        "md_path": md_path,
        "chunk_dir": UPLOAD_CHUNK_DIR,
        "chunk_json": chunk_json,
        "ocr_elapsed": elapsed,
        "source": "uploaded",
    }


def prepare_uploaded_document(file_name: str, data: bytes, table_format: str = "html") -> dict[str, Any]:
    existing = find_existing_ocr(file_name)
    if existing:
        doc_id, md_path = existing
        return prepare_existing_document(doc_id, md_path)

    saved_pdf = save_uploaded_pdf(file_name, data)
    return run_uploaded_pdf_ocr(saved_pdf, table_format=table_format)
