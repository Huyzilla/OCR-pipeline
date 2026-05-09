"""
Unified OCR pipeline: crop header → OCR (marker) → post-processing
Processes each PDF file through the full pipeline before moving to the next.
"""
from __future__ import annotations

import argparse
import tempfile
import time
from pathlib import Path

from ocr.crop_header import process_one_pdf as crop_one_pdf
from ocr.ocr import run_marker_convert, extract_pdf_folder_name
from ocr.post_processing import process_markdown_file


def process_single_pdf(
    input_pdf: Path,
    output_dir: Path,
    buffer_ratio: float = 0.005,
    fallback_ratio: float = 0.10,
    html_tables: bool = True,
) -> float:
    """
    Full pipeline for one PDF: crop → OCR → post-process.
    Returns elapsed time in seconds.
    """
    start = time.time()

    # --- Step 1: Crop header ---
    with tempfile.TemporaryDirectory() as tmp_dir:
        cropped_pdf = Path(tmp_dir) / f"{input_pdf.stem}_cropped.pdf"
        crop_one_pdf(
            input_pdf=input_pdf,
            output_pdf=cropped_pdf,
            buffer_ratio=buffer_ratio,
            fallback_ratio=fallback_ratio,
        )

        # --- Step 2: OCR with marker ---
        _, md_path, _ = run_marker_convert(
            pdf_path=cropped_pdf,
            out_root=output_dir,
            html_tables=html_tables,
        )

    # --- Step 3: Post-process markdown ---
    changed = process_markdown_file(md_path)
    if changed:
        print(f"  [post-process] Updated {md_path.name}")

    elapsed = time.time() - start
    return elapsed


def run_pipeline(
    input_dir: Path,
    output_dir: Path,
    buffer_ratio: float = 0.005,
    fallback_ratio: float = 0.10,
    html_tables: bool = True,
) -> None:
    """Process all PDFs in a folder through the full pipeline."""
    all_pdf_files = sorted(input_dir.glob("*.pdf"))
    if not all_pdf_files:
        raise FileNotFoundError(f"Khong tim thay file PDF trong: {input_dir}")

    # Resume: skip files that already have output
    pdf_files: list[Path] = []
    skipped = 0
    for pdf_path in all_pdf_files:
        folder_name = extract_pdf_folder_name(pdf_path)
        done_md = output_dir / folder_name / "main.md"
        if done_md.exists() and done_md.stat().st_size > 0:
            skipped += 1
            continue
        pdf_files.append(pdf_path)

    print(f"Input:  {input_dir}")
    print(f"Output: {output_dir}")
    print(f"Table format: {'HTML' if html_tables else 'Markdown'}")
    print(f"Tim thay {len(all_pdf_files)} file PDF")
    print(f"Bo qua {skipped} file da xu ly")
    print(f"Can chay {len(pdf_files)} file\n")

    if not pdf_files:
        print("Khong con file can xu ly.")
        return

    success = 0
    failed = 0
    times: list[float] = []

    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"[{i:03d}/{len(pdf_files):03d}] {pdf_path.name}", flush=True)
        try:
            elapsed = process_single_pdf(
                input_pdf=pdf_path,
                output_dir=output_dir,
                buffer_ratio=buffer_ratio,
                fallback_ratio=fallback_ratio,
                html_tables=html_tables,
            )
            times.append(elapsed)
            avg_time = sum(times) / len(times)
            remaining = len(pdf_files) - i
            eta_sec = avg_time * remaining
            print(f"  OK {elapsed:.1f}s | avg:{avg_time:.1f}s | ETA: {int(eta_sec//60)}m {int(eta_sec%60):02d}s")
            success += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"OCR PIPELINE SUMMARY")
    print(f"{'='*60}")
    print(f"Thanh cong: {success}/{len(pdf_files)}")
    print(f"That bai:   {failed}/{len(pdf_files)}")
    if times:
        total = sum(times)
        print(f"Tong thoi gian: {int(total//60)}m {int(total%60):02d}s")
        print(f"Avg/file: {sum(times)/len(times):.1f}s")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="OCR pipeline: crop header -> marker OCR -> post-process (per-file)"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input_pdf", help="Duong dan mot file PDF")
    group.add_argument("--input_dir", help="Thu muc chua cac file PDF")

    parser.add_argument("--output_dir", default="outputs", help="Thu muc luu ket qua (default: outputs)")
    parser.add_argument("--buffer_ratio", type=float, default=0.005, help="Buffer ratio cho crop header")
    parser.add_argument("--fallback_ratio", type=float, default=0.10, help="Fallback ratio khi khong detect table")
    parser.add_argument(
        "--table_format", choices=["markdown", "html"], default="html",
        help="Format bang: 'markdown' hoac 'html' (default: html)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    html_tables = args.table_format == "html"

    if args.input_pdf:
        pdf_path = Path(args.input_pdf)
        if not pdf_path.exists():
            raise FileNotFoundError(f"Khong tim thay file: {pdf_path}")
        elapsed = process_single_pdf(
            input_pdf=pdf_path,
            output_dir=output_dir,
            buffer_ratio=args.buffer_ratio,
            fallback_ratio=args.fallback_ratio,
            html_tables=html_tables,
        )
        print(f"Done! {elapsed:.1f}s")
    else:
        input_dir = Path(args.input_dir)
        if not input_dir.exists():
            raise FileNotFoundError(f"Khong tim thay thu muc: {input_dir}")
        run_pipeline(
            input_dir=input_dir,
            output_dir=output_dir,
            buffer_ratio=args.buffer_ratio,
            fallback_ratio=args.fallback_ratio,
            html_tables=html_tables,
        )


if __name__ == "__main__":
    main()
