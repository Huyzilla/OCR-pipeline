from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def ensure_marker_single() -> Path:
    marker_single = Path(sys.executable).parent / "marker_single"
    if marker_single.exists():
        return marker_single

    print("Khong tim thay marker_single, dang cai marker-pdf...")
    install_cmd = [sys.executable, "-m", "pip", "install", "marker-pdf"]
    install_result = subprocess.run(install_cmd, capture_output=True, text=True)
    if install_result.returncode != 0:
        print(install_result.stdout[-2000:])
        print(install_result.stderr[-2000:])
        raise RuntimeError("Cai marker-pdf that bai")

    marker_single = Path(sys.executable).parent / "marker_single"
    if not marker_single.exists():
        raise FileNotFoundError("Da cai marker-pdf nhung khong tim thay marker_single")
    return marker_single


def run_marker_single(
    marker_single: Path,
    pdf_path: Path,
    out_root: Path,
    page_range: str | None,
    timeout: int,
) -> tuple[int, float, Path, str, str]:
    cmd = [
        str(marker_single),
        str(pdf_path),
        "--output_dir",
        str(out_root),
        "--output_format",
        "markdown",
        "--disable_multiprocessing",
    ]
    if page_range:
        cmd.extend(["--page_range", page_range])

    print("Lenh:", " ".join(cmd))
    start = time.time()
    if timeout > 0:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    else:
        result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start

    base_name = pdf_path.stem
    md_path = out_root / base_name / f"{base_name}.md"
    return result.returncode, elapsed, md_path, result.stdout, result.stderr


def process_folder(
    input_dir: Path,
    out_root: Path,
    marker_single: Path,
    page_range: str | None,
    timeout: int,
) -> None:
    pdf_files = sorted(input_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"Khong tim thay file PDF trong: {input_dir}")

    print(f"Tim thay {len(pdf_files)} file PDF trong {input_dir}")
    success = 0
    failed = 0

    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Dang OCR: {pdf_path.name}")
        try:
            code, elapsed, md_path, stdout, stderr = run_marker_single(
                marker_single=marker_single,
                pdf_path=pdf_path,
                out_root=out_root,
                page_range=page_range,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            print(f"  TIMEOUT sau {timeout}s")
            failed += 1
            continue

        print(f"  Return code: {code} | Thoi gian: {elapsed:.1f}s")
        if code == 0 and md_path.exists():
            print(f"  OK -> Markdown: {md_path}")
            success += 1
        else:
            print("  FAIL: khong tao duoc markdown")
            if stderr:
                print(stderr[-1500:])
            elif stdout:
                print(stdout[-1500:])
            failed += 1

    print("\n=== OCR SUMMARY ===")
    print(f"Thanh cong: {success}")
    print(f"That bai  : {failed}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Marker OCR for one PDF or a folder.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input_pdf", help="Path to one cropped input PDF")
    group.add_argument("--input_dir", help="Folder containing cropped PDFs")

    parser.add_argument(
        "--output_dir",
        default="/media/data3/users/huytq/huy/outputs_marker_single",
        help="Directory to store Marker outputs",
    )
    parser.add_argument(
        "--page_range",
        default=None,
        help="Optional page range for marker_single, e.g. '0,1-3'",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=0,
        help="Timeout in seconds (0 means no timeout)",
    )
    args = parser.parse_args()

    out_root = Path(args.output_dir)
    out_root.mkdir(parents=True, exist_ok=True)

    marker_single = ensure_marker_single()

    if args.input_pdf:
        pdf_path = Path(args.input_pdf)
        if not pdf_path.exists():
            raise FileNotFoundError(f"Khong tim thay file PDF: {pdf_path}")

        print("Dang chay Marker cho 1 file PDF...")
        try:
            code, elapsed, md_path, stdout, stderr = run_marker_single(
                marker_single=marker_single,
                pdf_path=pdf_path,
                out_root=out_root,
                page_range=args.page_range,
                timeout=args.timeout,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Marker OCR timeout sau {args.timeout}s")

        print(f"Return code: {code}")
        print(f"Thoi gian: {elapsed:.1f}s")

        if code == 0 and md_path.exists():
            print(f"OK -> Markdown: {md_path}")
            md_text = md_path.read_text(encoding="utf-8", errors="ignore")
            print(f"Do dai markdown: {len(md_text)} ky tu")
            print("\nPreview 1000 ky tu dau:")
            print(md_text[:1000])
        else:
            print("FAIL: khong tao duoc markdown")
            if stderr:
                print(stderr[-2000:])
            elif stdout:
                print(stdout[-2000:])
            raise RuntimeError("Marker OCR that bai")
    else:
        input_dir = Path(args.input_dir)
        if not input_dir.exists():
            raise FileNotFoundError(f"Khong tim thay thu muc: {input_dir}")

        process_folder(
            input_dir=input_dir,
            out_root=out_root,
            marker_single=marker_single,
            page_range=args.page_range,
            timeout=args.timeout,
        )


if __name__ == "__main__":
    main()
