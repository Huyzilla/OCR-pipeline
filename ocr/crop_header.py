from __future__ import annotations

import argparse
from pathlib import Path

import fitz
import pdfplumber


def find_crop_ratio_with_pdfplumber(pdf_path: Path, buffer_ratio: float = 0.005) -> float | None:
    with pdfplumber.open(str(pdf_path)) as pdf:
        if not pdf.pages:
            return None

        first_page = pdf.pages[0]
        tables = first_page.find_tables()
        if not tables:
            return None

        # bbox = (x0, top, x1, bottom)
        first_table_bbox = tables[0].bbox
        page_height = first_page.height
        table_bottom = first_table_bbox[3]
        crop_ratio = (table_bottom / page_height) + buffer_ratio
        return min(max(crop_ratio, 0.0), 0.95)


def crop_pdf_top(input_pdf: Path, output_pdf: Path, crop_ratio: float) -> None:
    """Crop top area from all pages and save to a new PDF."""
    doc = fitz.open(str(input_pdf))
    for page in doc:
        rect = page.rect
        crop_rect = fitz.Rect(
            rect.x0,
            rect.y0 + rect.height * crop_ratio,
            rect.x1,
            rect.y1,
        )
        page.set_cropbox(crop_rect)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_pdf))
    doc.close()


def process_one_pdf(
    input_pdf: Path,
    output_pdf: Path,
    buffer_ratio: float,
    fallback_ratio: float,
) -> tuple[Path, Path, float]:
    crop_ratio = find_crop_ratio_with_pdfplumber(input_pdf, buffer_ratio)
    if crop_ratio is None:
        crop_ratio = fallback_ratio
        print(
            f"[{input_pdf.name}] Khong tim thay table o trang 1 -> fallback crop_ratio={crop_ratio:.4f}"
        )

    crop_pdf_top(input_pdf, output_pdf, crop_ratio)
    return input_pdf, output_pdf, crop_ratio


def process_folder(
    input_dir: Path,
    output_dir: Path,
    buffer_ratio: float,
    fallback_ratio: float,
) -> None:
    pdf_files = sorted(input_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"Khong tim thay file PDF trong: {input_dir}")

    print(f"Tim thay {len(pdf_files)} file PDF trong {input_dir}")
    success = 0
    failed = 0

    for i, input_pdf in enumerate(pdf_files, 1):
        output_pdf = output_dir / f"{input_pdf.stem}_cropped.pdf"
        print(f"\n[{i}/{len(pdf_files)}] Dang crop: {input_pdf.name}")
        try:
            in_path, out_path, ratio = process_one_pdf(
                input_pdf=input_pdf,
                output_pdf=output_pdf,
                buffer_ratio=buffer_ratio,
                fallback_ratio=fallback_ratio,
            )
            print(f"  OK -> {out_path} | ratio={ratio:.4f}")
            success += 1
        except Exception as exc:
            print(f"  FAIL -> {exc}")
            failed += 1

    print("\n=== CROP HEADER SUMMARY ===")
    print(f"Thanh cong: {success}")
    print(f"That bai  : {failed}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute crop ratio from page-1 table and create cropped PDF(s)."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input_pdf", help="Path to one input PDF")
    group.add_argument("--input_dir", help="Folder containing input PDFs")

    parser.add_argument(
        "--output_pdf",
        default=None,
        help="Path to output cropped PDF (default: <input_stem>_cropped.pdf)",
    )
    parser.add_argument(
        "--output_dir",
        default=None,
        help="Output folder for cropped PDFs when using --input_dir",
    )
    parser.add_argument(
        "--buffer_ratio",
        type=float,
        default=0.005,
        help="Extra ratio added under detected table bottom",
    )
    parser.add_argument(
        "--fallback_ratio",
        type=float,
        default=0.10,
        help="Fallback ratio when no table is detected on page 1",
    )

    args = parser.parse_args()

    if args.input_pdf:
        input_pdf = Path(args.input_pdf)
        if not input_pdf.exists():
            raise FileNotFoundError(f"Khong tim thay file: {input_pdf}")

        if args.output_pdf:
            output_pdf = Path(args.output_pdf)
        else:
            output_pdf = input_pdf.with_name(f"{input_pdf.stem}_cropped.pdf")

        in_path, out_path, ratio = process_one_pdf(
            input_pdf=input_pdf,
            output_pdf=output_pdf,
            buffer_ratio=args.buffer_ratio,
            fallback_ratio=args.fallback_ratio,
        )

        print("=== CROP HEADER DONE ===")
        print(f"Input : {in_path}")
        print(f"Output: {out_path}")
        print(f"Crop ratio: {ratio:.4f}")
    else:
        input_dir = Path(args.input_dir)
        if not input_dir.exists():
            raise FileNotFoundError(f"Khong tim thay thu muc: {input_dir}")

        if args.output_dir:
            output_dir = Path(args.output_dir)
        else:
            output_dir = input_dir / "cropped_pdfs"
        output_dir.mkdir(parents=True, exist_ok=True)

        process_folder(
            input_dir=input_dir,
            output_dir=output_dir,
            buffer_ratio=args.buffer_ratio,
            fallback_ratio=args.fallback_ratio,
        )


if __name__ == "__main__":
    main()
