import argparse
import re
from pathlib import Path


def _heading_level(numbering: str, max_level: int = 6) -> int:
    parts = [p for p in numbering.rstrip('.').split('.') if p]
    return min(len(parts), max_level) if parts else 1


def normalize_markdown_lines(lines: list[str]) -> list[str]:
    """
    Normalize markdown headings and convert list bullets from '-' to '*'.

    Rules:
    - Convert numbered bold headings like '**1.2 Title**' (or with leading #) to markdown headings.
    - Re-normalize existing headings that contain numbering.
    - Convert list lines that start with '-' to '*'.
    """
    new_lines: list[str] = []

    heading_pattern = r"^\s*(#{1,6})?\s*\*\*\s*(\d+(?:\.\d+)*\.?)\s+(.+?)\s*\*\*\s*$"

    for line in lines:
        # Case 1: numbered bold headings (Viettel-AI-Race style)
        match = re.match(heading_pattern, line)
        if match:
            _, numbering, text = match.groups()
            text = text.strip()
            if text:
                level = _heading_level(numbering)
                new_lines.append(f"{'#' * level} {text}\n")
            continue

        # Case 2: existing markdown heading -> normalize heading level if numbering detected
        if re.match(r"^\s*#{1,6}\s+", line):
            stripped = re.sub(r"^\s*#{1,6}\s+", "", line).strip()
            stripped_no_bold = stripped.replace("*", "")

            # Pattern: "1.2 Heading"
            m_front = re.match(r"^(\d+(?:\.\d+)*\.?)\s+(.*)$", stripped_no_bold)
            # Pattern: "Heading 1.2" (common OCR artifact)
            m_back = re.match(r"^(.*?)\s+(\d+(?:\.\d+)*\.?)$", stripped_no_bold)

            if m_front:
                numbering, text = m_front.groups()
                text = text.strip()
                if text:
                    level = _heading_level(numbering)
                    new_lines.append(f"{'#' * level} {text}\n")
                continue

            if m_back:
                text, numbering = m_back.groups()
                text = text.strip()
                if text:
                    level = _heading_level(numbering)
                    new_lines.append(f"{'#' * level} {text}\n")
                continue

            new_lines.append(stripped + "\n")
            continue

        # Case 3: list bullet '-' -> '*'
        if re.match(r"^\s*-\s+", line):
            converted = re.sub(r"^(\s*)-\s+", r"\1* ", line, count=1)
            new_lines.append(converted)
            continue

        # Case 4: keep line as-is
        new_lines.append(line)

    return new_lines


def process_markdown_file(file_path: Path) -> bool:
    try:
        original_lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
        processed_lines = normalize_markdown_lines(original_lines)

        if processed_lines != original_lines:
            file_path.write_text("".join(processed_lines), encoding="utf-8")
            return True
        return False
    except Exception as exc:
        print(f"[ERROR] {file_path}: {exc}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Post-process main.md files in a folder tree (overwrite in place)."
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        default="outputs",
        help="Root directory containing subfolders with main.md (default: outputs)",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    md_files = sorted(input_dir.rglob("main.md"))
    if not md_files:
        print(f"No main.md files found in: {input_dir}")
        return

    changed_count = 0
    for md_file in md_files:
        changed = process_markdown_file(md_file)
        if changed:
            changed_count += 1
            print(f"[UPDATED] {md_file}")

    print(f"Done. Processed {len(md_files)} files, updated {changed_count} files.")


if __name__ == "__main__":
    main()
