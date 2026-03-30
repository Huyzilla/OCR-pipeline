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
    for i, table in enumerate(html_tables):
        text_without_tables = text_without_tables.replace(table, f'\n\n[TABLE_{i}]\n\n') # Thay bảng bằng placeholder 

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config['text']['chunk_size'],
        chunk_overlap=config['text']['overlap'],
        separators=config['text']['separators']
    )

    raw_text_chunks = text_splitter.create_documents([text_without_tables])
    final_chunks = []

    for tc in raw_text_chunks: # Lọc từng chunk text 
        content = re.sub(r'\[TABLE_\d+\]', '', tc.page_content).strip()
        if len(content) >= config['text']['drop_too_short_chunk_size']:
            final_chunks.append({
                "page_content": content,
                "metadata": {
                    "doc_id": doc_id,
                    "chunk_type": "text"
                }
            })
        
    table_id_counter = 1
    for html_tb in html_tables:
        tb_chunks = chunk_html_table(
            html_tb, doc_id, table_id_counter, 
            config['table']['row_window'], 
            config['table']['row_overlap'], 
            config['table']['max_chunk_chars']
        )
        final_chunks.extend(tb_chunks)
        table_id_counter += 1

    return final_chunks

