import re
import importlib
from bs4 import BeautifulSoup
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    RecursiveCharacterTextSplitter = importlib.import_module(
        "langchain.text_splitter"
    ).RecursiveCharacterTextSplitter

def normalize_ocr_text(text):
    text = re.sub(r'(?<!\n)\n(?=[a-zđ])', ' ', text) # ghép các dòng bị xuống dòng sai
    text = re.sub(r'^(#+)\s+[\*\_]+(.*?)([\*\_]+)?\s*$', r'\1 \2', text, flags=re.MULTILINE) # Bỏ dấu *, _ thừa trong tiêu đề 
    text = re.sub(r'^-\s+([a-zđ]\))', r'\1', text, flags=re.MULTILINE) # Bỏ dấu - trước các mục kiểu a)
    text = re.sub(r'^-\s+([0-9]+\.)', r'\1', text, flags=re.MULTILINE) # Bỏ dấu - trước các danh sách đánh số 
    return text

def extract_heading_positions(text):
    positions = []
    for match in re.finditer(r'^#{1,6}\s+(.+)$', text, flags=re.MULTILINE):
        heading = match.group(1).strip()
        positions.append((match.start(), heading))
    return positions

def nearest_heading(heading_positions, start_idx):
    hint = None
    for pos, heading in heading_positions:
        if pos <= start_idx:
            hint = heading
        else:
            break
    return hint

def enrich_chunk_metadata(chunks, doc_id):
    """Attach ordering and linkage metadata for retrieval pipelines."""
    chunks.sort(key=lambda c: (c["metadata"].get("start_index", 0), c["metadata"].get("chunk_type", "text") != "text"))

    for idx, chunk in enumerate(chunks):
        meta = chunk["metadata"]
        chunk_id = f"{doc_id}::chunk::{idx}"
        section_hint = meta.get("section_hint") or "unknown"

        meta["chunk_index"] = idx
        meta["chunk_id"] = chunk_id
        meta["parent_id"] = f"{doc_id}::section::{section_hint}"
        meta["prev_chunk_id"] = f"{doc_id}::chunk::{idx - 1}" if idx > 0 else None
        meta["next_chunk_id"] = f"{doc_id}::chunk::{idx + 1}" if idx < len(chunks) - 1 else None

    return chunks

def apply_row_window(header, rows, doc_id, table_id, row_window, row_overlap, max_chars, join_str, suffix):
    chunks = []
    i = 0
    while i < len(rows):
        current_batch = []
        char_count = len(header) + len(suffix)
        end_row = i

        for j in range(i, min(i + row_window, len(rows))):
            row_len = len(rows[j]) + len(join_str)
            if char_count + row_len > max_chars and len(current_batch) > 0:
                break
            current_batch.append(rows[j])
            char_count += row_len
            end_row = j

        chunk_content = header + join_str.join(current_batch) + suffix
        chunks.append({
            "page_content": chunk_content,
            "metadata": {
                "doc_id": doc_id, 
                "chunk_type": "table",
                "table_id": table_id,
                "row_start": i,
                "row_end": end_row
            }
        })

        if end_row >= len(rows) - 1:
            break

        step = (end_row - i + 1) - row_overlap
        i += max(1, step)

    return chunks
    
def chunk_html_table(html_str, doc_id, table_id, row_window=10, row_overlap=2, max_chars=1800):
    soup = BeautifulSoup(html_str, "html.parser")
    thead = soup.find("thead")
    tbody = soup.find("tbody")
    
    if not tbody:
        rows = soup.find_all("tr")
        if len(rows) <= 1:
            return [{"page_content": html_str, "metadata": {"doc_id": doc_id, "chunk_type": "table", "table_id": table_id, "row_start": 0, "row_end": len(rows)-1}}]
        header_html = f"<table>\n<thead>\n{str(rows[0])}\n</thead>\n<tbody>\n"
        data_rows = [str(r) for r in rows[1:]]
    else:
        header_html = f"<table>\n{str(thead) if thead else ''}\n<tbody>\n"
        data_rows = [str(r) for r in tbody.find_all("tr")]
        
    return apply_row_window(header_html, data_rows, doc_id, table_id, row_window, row_overlap, max_chars, "\n", "\n</tbody>\n</table>")

def process_document(text, doc_id, config):
    text = normalize_ocr_text(text)

    html_table_pattern = r'(<table.*?>.*?</table>)'
    html_tables = re.findall(html_table_pattern, text, re.DOTALL)

    text_without_tables = text
    table_section_hints = {}
    for i, table in enumerate(html_tables):
        placeholder = f'\n\n[TABLE_{i}]\n\n'
        text_without_tables = text_without_tables.replace(table, placeholder, 1) # Thay bảng bằng placeholder

    heading_positions = extract_heading_positions(text_without_tables)
    table_marker_positions = {}
    for i in range(len(html_tables)):
        marker = f'[TABLE_{i}]'
        marker_idx = text_without_tables.find(marker)
        table_marker_positions[i] = marker_idx
        table_section_hints[i] = nearest_heading(heading_positions, marker_idx) if marker_idx >= 0 else None

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config['text']['chunk_size'],
        chunk_overlap=config['text']['overlap'],
        separators=config['text']['separators'],
        add_start_index=True,
    )

    raw_text_chunks = text_splitter.create_documents([text_without_tables])
    final_chunks = []

    for tc in raw_text_chunks: # Lọc từng chunk text 
        content = re.sub(r'\[TABLE_\d+\]', '', tc.page_content).strip()
        if len(content) >= config['text']['drop_too_short_chunk_size']:
            start_index = tc.metadata.get('start_index', 0)
            section_hint = nearest_heading(heading_positions, start_index)
            final_chunks.append({
                "page_content": content,
                "metadata": {
                    "doc_id": doc_id,
                    "chunk_type": "text",
                    "section_hint": section_hint,
                    "start_index": start_index,
                }
            })
        
    table_id_counter = 1
    for i, html_tb in enumerate(html_tables):
        tb_chunks = chunk_html_table(
            html_tb, doc_id, table_id_counter, 
            config['table']['row_window'], 
            config['table']['row_overlap'], 
            config['table']['max_chunk_chars']
        )
        section_hint = table_section_hints.get(i)
        for tb_idx, tb in enumerate(tb_chunks):
            tb["metadata"]["section_hint"] = section_hint
            tb["metadata"]["start_index"] = table_marker_positions.get(i, 0)
            tb["metadata"]["table_chunk_index"] = tb_idx
        final_chunks.extend(tb_chunks)
        table_id_counter += 1

    return enrich_chunk_metadata(final_chunks, doc_id)

