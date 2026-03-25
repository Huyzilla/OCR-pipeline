from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

try:
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.config.parser import ConfigParser
    from marker.output import text_from_rendered
    MARKER_AVAILABLE = True
except ImportError:
    MARKER_AVAILABLE = False


def ensure_marker_installed() -> None:
    """Đảm bảo marker-pdf được cài đặt."""
    if not MARKER_AVAILABLE:
        print("Không tìm thấy marker, đang cài marker-pdf...")
        install_cmd = [sys.executable, "-m", "pip", "install", "marker-pdf"]
        install_result = subprocess.run(install_cmd, capture_output=True, text=True)
        if install_result.returncode != 0:
            print(install_result.stdout[-2000:])
            print(install_result.stderr[-2000:])
            raise RuntimeError("Cài marker-pdf thất bại")
        print("Cài xong marker-pdf")


def _rows_from_table_html(table_html: str) -> list[str]:
    """Extract row HTML blocks from a table."""
    tbody_match = re.search(r"<tbody>(.*?)</tbody>", table_html, flags=re.DOTALL | re.IGNORECASE)
    body_html = tbody_match.group(1) if tbody_match else table_html
    return re.findall(r"<tr\b[^>]*>.*?</tr>", body_html, flags=re.DOTALL | re.IGNORECASE)


def _table_open_tag(table_html: str) -> str:
    match = re.search(r"<table\b[^>]*>", table_html, flags=re.IGNORECASE)
    return match.group(0) if match else "<table>"


def _normalize_header_row_to_data(row_html: str) -> str:
    """Convert TH cells in a row to TD cells."""
    row_html = re.sub(r"<th(\b[^>]*)>", r"<td\1>", row_html, flags=re.IGNORECASE)
    row_html = re.sub(r"</th>", "</td>", row_html, flags=re.IGNORECASE)
    return row_html


def _merge_two_tables(first_table: str, second_table: str) -> str:
    first_rows = _rows_from_table_html(first_table)
    second_rows = _rows_from_table_html(second_table)
    if not first_rows:
        return second_table
    if not second_rows:
        return first_table

    # Bảng tiếp theo thường lặp lại header; hạ TH -> TD để thành hàng dữ liệu thường.
    second_rows[0] = _normalize_header_row_to_data(second_rows[0])

    open_tag = _table_open_tag(first_table)
    merged_rows = "".join(first_rows + second_rows)
    return f"{open_tag}<tbody>{merged_rows}</tbody></table>"


def _has_text_between_tables(gap_text: str) -> bool:
    """Return True when there is meaningful text between two tables."""
    if not gap_text.strip():
        return False

    # Ignore common page separators/markers; anything else is treated as text.
    cleaned = re.sub(r"\f", "", gap_text)
    cleaned = re.sub(r"<!--\s*page[^>]*-->", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\{\s*#?page[^}]*\}", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\[\s*page\s*\d+\s*\]", "", cleaned, flags=re.IGNORECASE)
    return bool(cleaned.strip())


def merge_continued_html_tables(markdown_text: str) -> tuple[str, int]:
    """
    Merge consecutive HTML tables when there is no text between them.

    Rule:
    - If two tables are separated only by whitespace/page markers, treat them as one table.
    - Convert the first row of the lower table from header cells (TH) to normal cells (TD).
    """
    table_matches = list(re.finditer(r"<table\b[^>]*>.*?</table>", markdown_text, flags=re.DOTALL | re.IGNORECASE))
    if len(table_matches) < 2:
        return markdown_text, 0

    pieces: list[str] = []
    merged_count = 0

    prev_start = table_matches[0].start()
    prev_end = table_matches[0].end()
    current_table = table_matches[0].group(0)

    pieces.append(markdown_text[:prev_start])

    for match in table_matches[1:]:
        gap = markdown_text[prev_end:match.start()]
        next_table = match.group(0)

        if _has_text_between_tables(gap):
            pieces.append(current_table)
            pieces.append(gap)
            current_table = next_table
        else:
            current_table = _merge_two_tables(current_table, next_table)
            merged_count += 1

        prev_end = match.end()

    pieces.append(current_table)
    pieces.append(markdown_text[prev_end:])
    return "".join(pieces), merged_count


def run_marker_convert(
    pdf_path: Path,
    out_root: Path,
    html_tables: bool = True,
) -> tuple[float, Path, str]:
    """
    Dùng Python API của marker để convert PDF sang markdown.
    
    Args:
        pdf_path: Đường dẫn file PDF input
        out_root: Thư mục output
        html_tables: True = bảng HTML trong markdown, False = markdown tables
    
    Returns:
        (elapsed_time, output_md_path, markdown_text)
    """
    ensure_marker_installed()
    
    # Import here after ensuring marker is installed
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.config.parser import ConfigParser
    from marker.output import text_from_rendered
    
    # Config marker
    config = {
        "output_format": "markdown",
        "html_tables_in_markdown": html_tables,
    }
    config_parser = ConfigParser(config)
    converter = PdfConverter(
        config=config_parser.generate_config_dict(),
        artifact_dict=create_model_dict(),
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
        llm_service=config_parser.get_llm_service()
    )
    
    # Convert PDF
    start = time.time()
    rendered = converter(str(pdf_path))
    md_text, _, _ = text_from_rendered(rendered)

    if html_tables:
        md_text, merged_count = merge_continued_html_tables(md_text)
        if merged_count > 0:
            print(f"Đã ghép {merged_count} cặp bảng liền kề")

    elapsed = time.time() - start
    
    # Save markdown
    base_name = pdf_path.stem
    pdf_output_dir = out_root / base_name
    pdf_output_dir.mkdir(parents=True, exist_ok=True)
    md_path = pdf_output_dir / f"{base_name}.md"
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_text)
    
    return elapsed, md_path, md_text


def process_folder(
    input_dir: Path,
    out_root: Path,
    html_tables: bool = True,
) -> None:
    """Xử lý tất cả file PDF trong folder."""
    pdf_files = sorted(input_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"Không tìm thấy file PDF trong: {input_dir}")

    print(f"Tìm thấy {len(pdf_files)} file PDF trong {input_dir}")
    print(f"Format bảng: {'HTML' if html_tables else 'Markdown'}")
    success = 0
    failed = 0

    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Đang OCR: {pdf_path.name}")
        try:
            elapsed, md_path, md_text = run_marker_convert(
                pdf_path=pdf_path,
                out_root=out_root,
                html_tables=html_tables,
            )
            print(f"  ✓ Thành công | Thời gian: {elapsed:.1f}s | {len(md_text)} ký tự")
            print(f"    Output: {md_path}")
            success += 1
        except Exception as e:
            print(f"  ✗ Thất bại: {e}")
            failed += 1

    print("\n=== OCR SUMMARY ===")
    print(f"Thành công: {success}")
    print(f"Thất bại  : {failed}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chuyển đổi PDF sang Markdown bằng Marker.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input_pdf", help="Đường dẫn một file PDF")
    group.add_argument("--input_dir", help="Thư mục chứa các file PDF")

    parser.add_argument(
        "--output_dir",
        default="/media/data3/users/huytq/huy/outputs_marker_single",
        help="Thư mục lưu kết quả",
    )
    parser.add_argument(
        "--table_format",
        choices=["markdown", "html"],
        default="html",
        help="Format bảng: 'markdown' hoặc 'html' (mặc định: html)",
    )
    args = parser.parse_args()

    out_root = Path(args.output_dir)
    out_root.mkdir(parents=True, exist_ok=True)
    
    html_tables = args.table_format == "html"

    if args.input_pdf:
        pdf_path = Path(args.input_pdf)
        if not pdf_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file PDF: {pdf_path}")

        print("Đang chạy Marker cho 1 file PDF...")
        print(f"Format bảng: {'HTML' if html_tables else 'Markdown'}")
        
        try:
            elapsed, md_path, md_text = run_marker_convert(
                pdf_path=pdf_path,
                out_root=out_root,
                html_tables=html_tables,
            )
            print(f"✓ Thành công!")
            print(f"  Thời gian: {elapsed:.1f}s")
            print(f"  Kích thước: {len(md_text)} ký tự")
            print(f"  Output: {md_path}")
            print(f"\n--- Preview 1500 ký tự đầu ---")
            print(md_text[:1500])
        except Exception as e:
            print(f"✗ Thất bại: {e}")
            raise
    else:
        input_dir = Path(args.input_dir)
        if not input_dir.exists():
            raise FileNotFoundError(f"Không tìm thấy thư mục: {input_dir}")

        process_folder(
            input_dir=input_dir,
            out_root=out_root,
            html_tables=html_tables,
        )


if __name__ == "__main__":
    main()
