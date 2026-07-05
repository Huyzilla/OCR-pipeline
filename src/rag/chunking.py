from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

from bs4 import BeautifulSoup


class TableAwareChunker:
    def __init__(
        self,
        chunk_size: int = 512,
        overlap: int = 100,
        table_rows_per_chunk: int = 10,
        min_chunk_size: int = 50,
    ) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.table_rows_per_chunk = table_rows_per_chunk
        self.min_chunk_size = min_chunk_size

    @staticmethod
    def _clean_cell_text(text: str) -> str:
        return " ".join(text.split())
    
    @staticmethod
    def _build_metadata(
        document_id: str,
        hierarchy: List[str],
        chunk_type: str,
        extra: Dict | None = None,
    ) -> Dict:
        metadata: Dict = {
            "document_id": document_id,
            "hierarchy_path": " > ".join(hierarchy) if hierarchy else "",
            "chunk_type": chunk_type,
        }
        if extra:
            metadata.update(extra)
        return metadata

    def extract_and_chunk_table(
        self,
        html_table: str,
        context: str = "",
        document_id: str = "",
    ) -> List[Dict]:
        soup = BeautifulSoup(html_table, "html.parser")
        table = soup.find("table")

        if not table:
            return [
                {
                    "page_content": html_table,
                    "metadata": self._build_metadata(
                        document_id=document_id,
                        hierarchy=[context] if context else [],
                        chunk_type="table",
                        extra={
                            "table_id": 0,
                            "row_start": 0,
                            "row_end": 0,
                            "raw_html": html_table,
                            "column_headers": [],
                            "section_hint": context if context else "",
                        },
                    ),
                }
            ]

        headers: List[str] = []
        all_rows = table.find_all("tr")
        if not all_rows:
            return []

        header_row_idx = 0
        for idx, row in enumerate(all_rows):
            ths = row.find_all("th")
            if ths:
                headers = [
                    self._clean_cell_text(th.get_text(separator=" ", strip=True))
                    for th in ths
                ]
                header_row_idx = idx
                break

        if not headers:
            first_row_cells = all_rows[0].find_all(["td", "th"])
            headers = [
                self._clean_cell_text(cell.get_text(separator=" ", strip=True))
                for cell in first_row_cells
            ]
            header_row_idx = 0

        data_rows = all_rows[header_row_idx + 1 :]
        if not data_rows:
            return []

        parsed_rows: List[Dict] = []
        for row in data_rows:
            cells = row.find_all(["td", "th"])
            row_data = [
                self._clean_cell_text(cell.get_text(separator=" ", strip=True))
                for cell in cells
            ]
            if any(row_data):
                parsed_rows.append({"html": str(row), "cells": row_data})

        if not parsed_rows:
            return []

        table_chunks: List[Dict] = []
        i = 0

        while i < len(parsed_rows):
            current_rows: List[List[str]] = []
            current_html_rows: List[str] = []
            current_end = i

            while current_end < min(i + self.table_rows_per_chunk, len(parsed_rows)):
                current_rows.append(parsed_rows[current_end]["cells"])
                current_html_rows.append(parsed_rows[current_end]["html"])
                current_end += 1

            raw_html_parts = ["<table>"]
            if header_row_idx < len(all_rows):
                raw_html_parts.append(str(all_rows[header_row_idx]))
            raw_html_parts.extend(current_html_rows)
            raw_html_parts.append("</table>")
            raw_html = "\n".join(raw_html_parts)

            chunk_dict = self._format_table_chunk(
                context=context,
                headers=headers,
                rows=current_rows,
                chunk_index=len(table_chunks),
                document_id=document_id,
                row_start=i,
                row_end=current_end - 1,
                raw_html=raw_html,
            )
            table_chunks.append(chunk_dict)

            if current_end >= len(parsed_rows):
                break

            overlap_rows = min(2, current_end - i)
            step = (current_end - i) - overlap_rows
            i += max(1, step)

        return table_chunks

    def _format_table_chunk(
        self,
        context: str,
        headers: List[str],
        rows: List[List[str]],
        chunk_index: int,
        document_id: str,
        row_start: int,
        row_end: int,
        raw_html: str,
    ) -> Dict:
        formatted = ""

        if headers:
            formatted += "Cột: " + " | ".join([h for h in headers if h]) + "\n"

        if formatted:
            formatted += "\n"

        for i, row in enumerate(rows, 1):
            row_text = " | ".join(cell for cell in row if cell)
            if row_text:
                formatted += f"Dòng {i}: {row_text}\n"

        hierarchy = [h.strip() for h in context.split(">") if h.strip()] if context else []

        return {
            "page_content": formatted.strip(),
            "metadata": self._build_metadata(
                document_id=document_id,
                hierarchy=hierarchy,
                chunk_type="table",
                extra={
                    "table_id": chunk_index + 1,
                    "section_hint": context,
                    "row_start": row_start,
                    "row_end": row_end,
                    "table_part": chunk_index + 1,
                    "raw_html": raw_html,
                    "column_headers": headers,
                },
            ),
        }

    def process_document_with_tables(self, text: str, document_id: str) -> List[Dict]:
        all_chunks: List[Dict] = []
        parts = self._split_text_and_tables(text)

        current_heading_stack: List[tuple[int, str]] = []
        section_context = ""

        for part in parts:
            if part["type"] == "text":
                blocks, current_heading_stack = self._split_text_blocks_by_heading(
                    part["content"],
                    current_heading_stack,
                )
                current_hierarchy = [title for _, title in current_heading_stack]
                section_context = " > ".join(current_hierarchy) if current_hierarchy else ""

                for block_text, block_heading_stack in blocks:
                    block_hierarchy = [title for _, title in block_heading_stack]
                    text_chunks = self._process_text_section(
                        block_text,
                        document_id,
                        block_hierarchy,
                    )
                    all_chunks.extend(text_chunks)

            elif part["type"] == "table":
                context = section_context if section_context else "Table data"
                table_chunks = self.extract_and_chunk_table(
                    part["content"],
                    context,
                    document_id,
                )
                all_chunks.extend(table_chunks)

        for i, chunk in enumerate(all_chunks):
            chunk.setdefault("metadata", {})["chunk_index"] = i

        return all_chunks

    def _split_text_blocks_by_heading(
        self,
        text: str,
        initial_heading_stack: List[tuple[int, str]],
    ) -> tuple[List[tuple[str, List[tuple[int, str]]]], List[tuple[int, str]]]:
        lines = text.splitlines(keepends=True)
        active_heading_stack = initial_heading_stack.copy()

        blocks: List[tuple[str, List[tuple[int, str]]]] = []
        block_lines: List[str] = []
        block_heading_stack = active_heading_stack.copy()

        for line in lines:
            heading_match = re.match(r"^(#+)\s+(.+)$", line.strip())
            if heading_match:
                # Flush old block before switching context.
                old_block = "".join(block_lines).strip()
                if old_block:
                    blocks.append((old_block, block_heading_stack.copy()))

                level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()
                if level == 1:
                    active_heading_stack = [(1, heading_text)]
                else:
                    while active_heading_stack and active_heading_stack[-1][0] >= level:
                        active_heading_stack.pop()
                    active_heading_stack.append((level, heading_text))

                block_heading_stack = active_heading_stack.copy()
                block_lines = [line]
            else:
                block_lines.append(line)

        old_block = "".join(block_lines).strip()
        if old_block:
            blocks.append((old_block, block_heading_stack.copy()))

        return blocks, active_heading_stack

    def _split_text_and_tables(self, text: str) -> List[Dict]:
        parts: List[Dict] = []
        table_pattern = r"<table[^>]*>.*?</table>"

        last_end = 0
        for match in re.finditer(table_pattern, text, re.DOTALL | re.IGNORECASE):
            if match.start() > last_end:
                text_content = text[last_end : match.start()].strip()
                if text_content:
                    parts.append({"type": "text", "content": text_content})

            parts.append({"type": "table", "content": match.group()})
            last_end = match.end()

        if last_end < len(text):
            text_content = text[last_end:].strip()
            if text_content:
                parts.append({"type": "text", "content": text_content})

        if not parts:
            parts.append({"type": "text", "content": text})

        return parts

    def _process_text_section(self, text: str, document_id: str, hierarchy: List[str]) -> List[Dict]:
        chunks: List[Dict] = []
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        if not paragraphs:
            return chunks

        current_chunk_paras: List[str] = []
        current_size = 0

        for para in paragraphs:
            para_words = len(para.split())

            if current_size + para_words > self.chunk_size and current_chunk_paras:
                chunk_dict = self._create_text_chunk(
                    current_chunk_paras,
                    document_id,
                    hierarchy.copy(),
                    len(chunks),
                )
                chunks.append(chunk_dict)

                if self.overlap > 0 and current_chunk_paras:
                    # Paragraph-level overlap: keep the last paragraph as context for the next chunk.
                    current_chunk_paras = [current_chunk_paras[-1], para]
                    current_size = len(current_chunk_paras[-1].split()) + para_words
                else:
                    current_chunk_paras = [para]
                    current_size = para_words
            else:
                current_chunk_paras.append(para)
                current_size += para_words

        if current_chunk_paras and current_size >= self.min_chunk_size:
            chunk_dict = self._create_text_chunk(
                current_chunk_paras,
                document_id,
                hierarchy.copy(),
                len(chunks),
            )
            chunks.append(chunk_dict)

        return chunks

    def _create_text_chunk(
        self,
        paragraphs: List[str],
        document_id: str,
        hierarchy: List[str],
        chunk_index: int,
    ) -> Dict:
        context_header = " > ".join(hierarchy) if hierarchy else ""

        chunk_text = "\n\n".join(paragraphs)

        return {
            "page_content": chunk_text,
            "metadata": self._build_metadata(
                document_id=document_id,
                hierarchy=hierarchy,
                chunk_type="text",
                extra={
                    "chunk_index": chunk_index,
                },
            ),
        }


def chunk_single_markdown(chunker: TableAwareChunker, input_md: Path, doc_id: str) -> List[Dict]:
    text = input_md.read_text(encoding="utf-8", errors="ignore")
    return chunker.process_document_with_tables(text, doc_id)


def chunk_combined_markdown(chunker: TableAwareChunker, input_md: Path) -> List[Dict]:
    text = input_md.read_text(encoding="utf-8", errors="ignore")

    # Same splitting style as Viettel-AI-Race embed_document.py
    doc_pattern = r"# (Public_\d+)"
    doc_splits = re.split(doc_pattern, text)

    all_chunks: List[Dict] = []
    current_doc_id = "UNKNOWN"

    for segment in doc_splits:
        segment = segment.strip()
        if not segment:
            continue

        if re.match(r"^Public_\d+$", segment):
            current_doc_id = segment
            continue

        chunks = chunker.process_document_with_tables(segment, current_doc_id)
        all_chunks.extend(chunks)

    return all_chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Viettel-AI-Race style chunking only")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input_md", type=str, help="Path to a single markdown file")
    group.add_argument(
        "--input_combined",
        type=str,
        help="Path to combined markdown with '# Public_XXX' sections",
    )

    parser.add_argument("--output_json", type=str, required=True, help="Output chunk JSON path")
    parser.add_argument("--doc_id", type=str, default=None, help="Document id for --input_md")
    parser.add_argument("--chunk_size", type=int, default=512)
    parser.add_argument("--overlap", type=int, default=100)
    parser.add_argument("--table_rows", type=int, default=10)
    parser.add_argument("--min_chunk_size", type=int, default=50)

    args = parser.parse_args()

    chunker = TableAwareChunker(
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        table_rows_per_chunk=args.table_rows,
        min_chunk_size=args.min_chunk_size,
    )

    if args.input_md:
        input_path = Path(args.input_md)
        if not input_path.exists():
            raise FileNotFoundError(f"Input markdown not found: {input_path}")
        doc_id = args.doc_id or input_path.stem
        chunks = chunk_single_markdown(chunker, input_path, doc_id)
    else:
        input_path = Path(args.input_combined)
        if not input_path.exists():
            raise FileNotFoundError(f"Input markdown not found: {input_path}")
        chunks = chunk_combined_markdown(chunker, input_path)

    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")

    text_count = sum(1 for c in chunks if c.get("metadata", {}).get("chunk_type") == "text")
    table_count = sum(1 for c in chunks if c.get("metadata", {}).get("chunk_type") == "table")

    print(f"OK -> {output_path}")
    print(f"Total: {len(chunks)} | Text: {text_count} | Table: {table_count}")


if __name__ == "__main__":
    main()
