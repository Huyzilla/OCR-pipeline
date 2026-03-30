from __future__ import annotations

import argparse
import re
from pathlib import Path


def normalize_ocr_markdown(text: str) -> str:
    # Remove bold/italic markers around heading text, e.g. "## **Title**"
    text = re.sub(
        r"^(#+)\s+[\*_]+\s*(.*?)\s*[\*_]+\s*$",
        r"\1 \2",
        text,
        flags=re.MULTILINE,
    )

    def recalculate_heading_level(match: re.Match[str]) -> str:
        numbering = match.group(1)
        title = match.group(2).strip()

        # Heading level is based on depth of numbering, e.g. 1.2.3 -> ###
        level = len(numbering.strip(".").split("."))
        level = min(level, 6)
        return f"{'#' * level} {numbering} {title}".rstrip()

    def build_heading(numbering: str, title: str) -> str:
        level = len(numbering.strip(".").split("."))
        level = min(level, 6)
        return f"{'#' * level} {numbering} {title.strip()}".rstrip()

    # Rebuild heading level from numeric numbering.
    text = re.sub(
        r"^#+\s+([0-9]+(?:\.[0-9]+)*\.?)[ \t]+(.*)$",
        recalculate_heading_level,
        text,
        flags=re.MULTILINE,
    )

    # Normalize cases like "## *1.2.1 Title" -> "### 1.2.1 Title"
    text = re.sub(
        r"^#+\s+[\*_]+\s*([0-9]+(?:\.[0-9]+)*\.?)[ \t]+(.*)$",
        lambda m: build_heading(m.group(1), m.group(2)),
        text,
        flags=re.MULTILINE,
    )

    # Normalize list bullets accidentally prefixed with '- '.
    text = re.sub(r"^-\s+([a-zđ])\)", r"\1)", text, flags=re.MULTILINE)
    text = re.sub(r"^-\s+([0-9]+\.)", r"\1", text, flags=re.MULTILINE)

    return text


def process_file(path: Path, apply: bool) -> bool:
    original = path.read_text(encoding="utf-8", errors="ignore")
    normalized = normalize_ocr_markdown(original)
    changed = normalized != original

    if changed and apply:
        path.write_text(normalized, encoding="utf-8")

    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize OCR markdown headings and list markers.")
    parser.add_argument(
        "--input_dir",
        default="/media/data3/users/huytq/huy/outputs_marker_single",
        help="Directory containing markdown files",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write normalized content back to files (default is dry-run)",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    md_files = sorted(input_dir.rglob("*.md"))

    if not md_files:
        raise FileNotFoundError(f"No markdown files found in: {input_dir}")

    changed_files: list[Path] = []
    for md_file in md_files:
        if process_file(md_file, apply=args.apply):
            changed_files.append(md_file)

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"Mode: {mode}")
    print(f"Total files: {len(md_files)}")
    print(f"Changed files: {len(changed_files)}")

    if changed_files:
        print("Sample changed files:")
        for p in changed_files[:10]:
            print(f"- {p}")


if __name__ == "__main__":
    main()
