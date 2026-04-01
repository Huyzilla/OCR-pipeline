#!/usr/bin/env python3
"""
Batch OCR runner with new output structure.
Runs OCR on all PDFs in input folder with proper folder naming and structure.
"""
import sys
import argparse
from pathlib import Path

# Import OCR functions
from ocr import run_marker_convert, process_folder


def main():
    parser = argparse.ArgumentParser(description="Run batch OCR on all PDFs with new structure")
    parser.add_argument(
        "--input_dir",
        default="/media/data3/users/huytq/huy/input/cropped_pdfs",
        help="Input folder containing PDFs",
    )
    parser.add_argument(
        "--output_dir",
        default="/media/data3/users/huytq/huy/outputs",
        help="Output folder for OCR results",
    )
    parser.add_argument(
        "--table_format",
        choices=["markdown", "html"],
        default="html",
        help="Table format: 'markdown' or 'html' (default: html)",
    )
    parser.add_argument(
        "--start_from",
        type=int,
        default=1,
        help="Start from Nth PDF (useful for re-running from specific point)",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    html_tables = args.table_format == "html"

    print(f"📁 Input:  {input_dir}")
    print(f"📁 Output: {output_dir}")
    print(f"📊 Table format: {'HTML' if html_tables else 'Markdown'}")
    print()

    # Get all PDFs
    pdf_files = sorted(input_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ No PDF files found in {input_dir}")
        sys.exit(1)

    print(f"📄 Found {len(pdf_files)} PDFs")
    
    # Filter to start from specified index
    if args.start_from > 1:
        pdf_files = pdf_files[args.start_from - 1:]
        print(f"⏭️  Starting from PDF #{args.start_from}")
    
    print()

    success = 0
    failed = 0
    failed_files = []

    for i, pdf_path in enumerate(pdf_files, args.start_from):
        print(f"[{i:03d}/{len(pdf_files):03d}] Processing: {pdf_path.name}", end=" ... ", flush=True)
        try:
            elapsed, md_path, md_text = run_marker_convert(
                pdf_path=pdf_path,
                out_root=output_dir,
                html_tables=html_tables,
            )
            print(f"✅ ({elapsed:.1f}s, {len(md_text)} chars)")
            success += 1
        except Exception as e:
            print(f"❌ ERROR: {str(e)[:60]}")
            failed += 1
            failed_files.append(pdf_path.name)

    print("\n" + "="*60)
    print(f"📊 SUMMARY")
    print("="*60)
    print(f"✅ Success: {success}")
    print(f"❌ Failed:  {failed}")
    print(f"📈 Total:   {success + failed}")
    
    if failed_files:
        print(f"\n❌ Failed files:")
        for fname in failed_files:
            print(f"   - {fname}")


if __name__ == "__main__":
    main()
