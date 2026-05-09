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


def extract_pdf_folder_name(pdf_path: Path) -> str:
    """
    Extract folder name from PDF path with special handling:
    - Removes '_cropped' suffix if present
    - Converts filename to header format (e.g., Public283 → Public_283)
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        Folder name suitable for output (e.g., 'Public283' or 'Public283_cropped' → 'Public283')
    """
    base_name = pdf_path.stem
    # Remove _cropped suffix if present
    if base_name.endswith("_cropped"):
        base_name = base_name[:-len("_cropped")]
    return base_name


def format_pdf_header(folder_name: str) -> str:
    """
    Convert folder name to markdown header format.
    E.g., 'Public283' → '# Public_283'
    """
    # Insert underscore before numbers at the end if not already present
    match = re.match(r"^([A-Za-z]+)(\d+)$", folder_name)
    if match:
        prefix, number = match.groups()
        return f"# {prefix}_{number}"
    return f"# {folder_name}"


def replace_image_placeholders(md_text: str, image_count: int) -> str:
    """
    Replace image placeholders with correct format: ![](images/imageX.jpg)
    Assumes images are numbered sequentially from 1.
    
    Args:
        md_text: Original markdown text
        image_count: Number of images to generate placeholders for
    
    Returns:
        Markdown with image placeholders
    """
    # Find all image-like patterns in markdown and replace them
    # This is a simple approach: if markdown has ![...](...)  patterns,
    # we'll replace them with sequential image references
    image_pattern = r"!\[.*?\]\(.*?\)"
    images = re.findall(image_pattern, md_text)
    
    # Replace found images with correct format
    for i, _ in enumerate(images[:image_count], 1):
        md_text = md_text.replace(images[i-1], f"![](images/image{i}.jpg)", 1)
    
    return md_text


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
    
    # Manage GPU memory to avoid OOM
    import os
    os.environ["TORCH_CUDA_EMPTY_CACHE"] = "1"
    try:
        import torch
        torch.cuda.empty_cache()
        # Reduce to CPU-only if memory issues persist
        # os.environ["CUDA_VISIBLE_DEVICES"] = ""
    except:
        pass
    
    # Config marker with memory optimization
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
    
    # Extract folder name (remove _cropped if present)
    folder_name = extract_pdf_folder_name(pdf_path)
    pdf_output_dir = out_root / folder_name
    
    # Create directory structure
    pdf_output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = pdf_output_dir / "images"
    images_dir.mkdir(exist_ok=True)
    
    # Count existing images and prepare header
    header = format_pdf_header(folder_name)
    
    # Process markdown: add header and fix image references
    image_count = len(re.findall(r"!\[.*?\]\(.*?\)", md_text))
    md_text = replace_image_placeholders(md_text, image_count)
    final_md = f"{header}\n\n{md_text}"
    
    # Save main.md
    md_path = pdf_output_dir / "main.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(final_md)
    
    return elapsed, md_path, final_md


def process_folder(
    input_dir: Path,
    out_root: Path,
    html_tables: bool = True,
) -> None:
    """Xử lý tất cả file PDF trong folder với timing chi tiết."""
    all_pdf_files = sorted(input_dir.glob("*.pdf"))
    if not all_pdf_files:
        raise FileNotFoundError(f"Không tìm thấy file PDF trong: {input_dir}")

    # Resume mode: skip files that already have outputs/<PublicXXX>/main.md
    pdf_files: list[Path] = []
    skipped_files = 0
    for pdf_path in all_pdf_files:
        folder_name = extract_pdf_folder_name(pdf_path)
        done_md = out_root / folder_name / "main.md"
        if done_md.exists() and done_md.stat().st_size > 0:
            skipped_files += 1
            continue
        pdf_files.append(pdf_path)

    print(f"📁 Input:  {input_dir}")
    print(f"📁 Output: {out_root}")
    print(f"📊 Table format: {'HTML' if html_tables else 'Markdown'}")
    print(f"📄 Tìm thấy {len(all_pdf_files)} file PDF")
    print(f"⏭️  Bỏ qua {skipped_files} file đã xử lý")
    print(f"▶️  Cần chạy {len(pdf_files)} file\n")

    if not pdf_files:
        print("✅ Không còn file cần xử lý. Batch đã hoàn tất.")
        return

    print(f"🚀 Bắt đầu từ file: {pdf_files[0].name}\n")
    
    success = 0
    failed = 0
    times: list[float] = []
    batch_start = time.time()

    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"[{i:03d}/{len(pdf_files):03d}] {pdf_path.name[:40]:40s}", end=" ... ", flush=True)
        try:
            elapsed, md_path, md_text = run_marker_convert(
                pdf_path=pdf_path,
                out_root=out_root,
                html_tables=html_tables,
            )
            times.append(elapsed)
            
            # Calculate stats
            avg_time = sum(times) / len(times)
            remaining = len(pdf_files) - i
            eta_sec = avg_time * remaining
            
            print(f"✅ {elapsed:6.1f}s", end="")
            if len(times) > 1:
                print(f" | avg:{avg_time:6.1f}s | ETA: {int(eta_sec//60):3d}m {int(eta_sec%60):02d}s")
            else:
                print()
            
            success += 1
        except Exception as e:
            error_msg = str(e)[:50]
            print(f"❌ ERROR: {error_msg}")
            failed += 1

    batch_elapsed = time.time() - batch_start
    
    print("\n" + "="*80)
    print(f"📊 OCR BATCH SUMMARY")
    print("="*80)
    print(f"✅ Thành công: {success}/{len(pdf_files)}")
    print(f"❌ Thất bại:   {failed}/{len(pdf_files)}")
    print(f"⏱️  Tổng thời gian: {int(batch_elapsed//60):3d}m {int(batch_elapsed%60):02d}s")
    
    if times:
        print(f"⏱️  Avg/file:       {sum(times)/len(times):6.1f}s")
        print(f"⏱️  Min/Max:        {min(times):6.1f}s / {max(times):6.1f}s")
    
    print("="*80)


def main() -> None:
    parser = argparse.ArgumentParser(description="Chuyển đổi PDF sang Markdown bằng Marker.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input_pdf", help="Đường dẫn một file PDF")
    group.add_argument("--input_dir", help="Thư mục chứa các file PDF")

    parser.add_argument(
        "--output_dir",
        default="/media/data3/users/huytq/huy/outputs",
        help="Thư mục lưu kết quả (mặc định: outputs/)",
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
            print(f"Thành công!")
            print(f"Thời gian: {elapsed:.1f}s")
        except Exception as e:
            print(f"Thất bại: {e}")
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
