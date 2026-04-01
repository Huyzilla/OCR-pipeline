from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from chunking import process_document


def default_config() -> dict[str, Any]:
    return {
        "text": {
            "chunk_size": 1200,
            "overlap": 300,
            "separators": ["\n\n", "\n", ". ", "; ", ": ", ") ", ", ", " "],
            "drop_too_short_chunk_size": 120,
        },
        "table": {
            "row_window": 10,
            "row_overlap": 2,
            "max_chunk_chars": 1800,
        },
    }


def load_config(config_path: str | None) -> dict[str, Any]:
    if not config_path:
        return default_config()

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Khong tim thay config file: {path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def process_one_file(input_md: Path, output_json: Path, config: dict[str, Any]) -> tuple[int, int, int]:
    text = input_md.read_text(encoding="utf-8", errors="ignore")
    chunks = process_document(text, doc_id=input_md.stem, config=config)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")

    text_count = sum(1 for c in chunks if c.get("metadata", {}).get("chunk_type") == "text")
    table_count = sum(1 for c in chunks if c.get("metadata", {}).get("chunk_type") == "table")
    return len(chunks), text_count, table_count


def process_folder(input_dir: Path, output_dir: Path, config: dict[str, Any]) -> None:
    md_files = sorted(input_dir.rglob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"Khong tim thay file .md trong: {input_dir}")

    print(f"Tim thay {len(md_files)} file markdown")
    success = 0
    failed = 0

    for i, md in enumerate(md_files, 1):
        rel = md.relative_to(input_dir)
        out = output_dir / rel.parent / f"{md.stem}_chunks.json"
        print(f"\n[{i}/{len(md_files)}] Dang chunk: {md}")
        try:
            total, text_count, table_count = process_one_file(md, out, config)
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
        default="/media/data3/users/huytq/huy/chunk_outputs",
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

        output_json = Path(args.output) if args.output else Path(args.output_dir) / f"{input_md.stem}_chunks.json"
        total, text_count, table_count = process_one_file(input_md, output_json, config)
        print(f"OK -> {output_json}")
        print(f"Tong: {total} | Text: {text_count} | Table: {table_count}")
    else:
        input_dir = Path(args.input_dir)
        if not input_dir.exists():
            raise FileNotFoundError(f"Khong tim thay thu muc: {input_dir}")
        process_folder(input_dir, Path(args.output_dir), config)


if __name__ == "__main__":
    main()
