from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rag.chunking import TableAwareChunker


def default_config() -> dict[str, Any]:
    return {
        "text": {
            "chunk_size": 512,
            "overlap": 100,
            "min_chunk_size": 20,
        },
        "table": {
            "row_window": 10,
        },
    }


def load_config(config_path: str | None) -> dict[str, Any]:
    config = default_config()

    if not config_path:
        return config

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Khong tim thay config file: {path}")

    with path.open("r", encoding="utf-8") as f:
        user_config = json.load(f)

    if "text" in user_config:
        config["text"].update(user_config["text"])
    if "table" in user_config:
        config["table"].update(user_config["table"])

    return config


def build_chunker(config: dict[str, Any]) -> TableAwareChunker:
    text_cfg = config.get("text", {})
    table_cfg = config.get("table", {})
    return TableAwareChunker(
        chunk_size=text_cfg.get("chunk_size", 512),
        overlap=text_cfg.get("overlap", 100),
        table_rows_per_chunk=table_cfg.get("row_window", 10),
        min_chunk_size=text_cfg.get("min_chunk_size", 50),
    )


def process_one_file(
    input_md: Path,
    output_json: Path,
    config: dict[str, Any],
    doc_id: str | None = None,
) -> tuple[int, int, int]:
    text = input_md.read_text(encoding="utf-8", errors="ignore")
    resolved_doc_id = doc_id or input_md.parent.name or input_md.stem
    chunker = build_chunker(config)
    chunks = chunker.process_document_with_tables(text, resolved_doc_id)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")

    text_count = sum(1 for c in chunks if c.get("metadata", {}).get("chunk_type") == "text")
    table_count = sum(1 for c in chunks if c.get("metadata", {}).get("chunk_type") == "table")
    return len(chunks), text_count, table_count


def process_folder(input_dir: Path, output_dir: Path, config: dict[str, Any]) -> None:
    # Viettel-AI-Race style: process only document roots named main.md.
    md_files = sorted(input_dir.rglob("main.md"))
    if not md_files:
        raise FileNotFoundError(f"Khong tim thay file main.md trong: {input_dir}")

    print(f"Tim thay {len(md_files)} file markdown")
    success = 0
    failed = 0

    for i, md in enumerate(md_files, 1):
        rel = md.relative_to(input_dir)
        out_parent = rel.parent if str(rel.parent) != "." else Path(md.parent.name)
        out = output_dir / out_parent / "main_chunks_viettel.json"
        doc_id = md.parent.name if md.parent.name else md.stem
        print(f"\n[{i}/{len(md_files)}] Dang chunk: {md}")
        try:
            total, text_count, table_count = process_one_file(md, out, config, doc_id=doc_id)
            print(f"  OK -> {out}")
            print(f"  Tong: {total} | Text: {text_count} | Table: {table_count}")
            success += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            failed += 1

    print("\n=== CHUNKING SUMMARY ===")
    print(f"Thanh cong: {success}")
    print(f"That bai  : {failed}")


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI chunking cho file markdown OCR")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input_md", help="Duong dan 1 file markdown")
    group.add_argument("--input_dir", help="Thu muc markdown")

    parser.add_argument(
        "--output",
        help="Output JSON khi dung --input_md",
    )
    parser.add_argument(
        "--output_dir",
        default="chunks_output_finals",
        help="Thu muc output khi dung --input_dir",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Config JSON tuy chon. Neu bo qua se dung default config",
    )
    args = parser.parse_args()

    config = load_config(args.config)

    if args.input_md:
        input_md = Path(args.input_md)
        if not input_md.exists():
            raise FileNotFoundError(f"Khong tim thay file: {input_md}")

        output_json = Path(args.output) if args.output else Path(args.output_dir) / "main_chunks_viettel.json"
        total, text_count, table_count = process_one_file(input_md, output_json, config, doc_id=input_md.parent.name)
        print(f"OK -> {output_json}")
        print(f"Tong: {total} | Text: {text_count} | Table: {table_count}")
    else:
        input_dir = Path(args.input_dir)
        if not input_dir.exists():
            raise FileNotFoundError(f"Khong tim thay thu muc: {input_dir}")
        process_folder(input_dir, Path(args.output_dir), config)


if __name__ == "__main__":
    main()
