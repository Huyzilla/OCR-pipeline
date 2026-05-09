# Pipeline RAG 

1. Hậu xử lý markdown sau khi OCR
2. Chunking
3. Indexing
4. RAG (retrieve, rerank, answer)

## 1. Hậu xử lý Markdown sau khi OCR

Đầu vào sau OCR là `outputs/PublicXXX/main.md`, thường có các vấn đề:
- Heading chưa đồng nhất  
- Bullet list bị rối định dạng  
- Bảng dữ liệu cần giữ dạng HTML để truy xuất sau này  

File `post_processing.py` được dùng để chuẩn hóa markdown theo format mong muốn trước khi chunking.

**Mục tiêu của hậu xử lý:**
- Giữ ngữ nghĩa và cấu trúc  
- Giảm nhiễu text do OCR  
- Giúp parser chunking xử lý heading và table chính xác hơn  

---

## 2. Chunking (`chunking.py`)

Chunker đang sử dụng là `TableAwareChunker` trong `chunking.py`.

### 2.1. Tách text và table

Tài liệu markdown được tách thành các phần:
- `type = text`  
- `type = table` (HTML table)  

Ví dụ: một tài liệu có văn bản → bảng → văn bản, sẽ được xử lý theo đúng thứ tự xuất hiện.

---

### 2.2. Chunk text

Text được chia theo paragraph và ngữ cảnh heading:
- Theo dõi hierarchy của heading để tạo metadata `hierarchy_path`  
- `chunk_size` và `min_chunk_size` điều chỉnh độ dài chunk  
- Có overlap theo paragraph: giữ paragraph cuối của chunk trước để đưa vào chunk sau  

**Metadata của text chunk:**
- `document_id`  
- `hierarchy_path`  
- `chunk_type = text`  
- `chunk_index`  

---
### 2.3. Chunk table

Bảng HTML được parse theo từng dòng:
- Lấy header  
- Parse từng dòng dữ liệu  
- Chia theo `table_rows_per_chunk` (có overlap giữa các dòng)  

Render bảng thành text theo format:
- Cột: ...  
- Dòng 1: ...  

**Metadata của table chunk:**
- `document_id`  
- `hierarchy_path`  
- `chunk_type = table`  
- `table_id`  
- `row_start`, `row_end`  
- `table_part`  
- `raw_html`  
- `column_headers`  

`raw_html` giúp giữ nguyên bảng gốc để LLM có thể đối chiếu khi cần.

---
## 3. Indexing (`indexing_chromadb.py`)

Dự án sử dụng ChromaDB để index các chunk.

### 3.1. Input

Thư mục `chunk_outputs_final_viettel`, mỗi `PublicXXX` có 1 file:
`main_chunks_viettel.json`

---

### 3.2. Xử lý metadata

Chroma không chấp nhận metadata dạng list/dict trực tiếp, nên có hàm `_sanitize_metadata`:
- `column_headers` (list) → chuyển thành chuỗi  
- Các list/dict khác → JSON string  
- Metadata rỗng → thêm `_source`  

---

### 3.3. Upsert vào Chroma

Mỗi batch gồm:
- `ids`  
- `documents`  
- `embeddings`  
- `metadatas`  

ID được prefix để tránh xung đột:
- viettel_v1_document_chunktype_chunkindex

---

### 3.4. Smoke test

Sau khi index xong, script chạy một query test để kiểm tra collection truy vấn được.

---

## 4. RAG Pipeline (`test.py`)

Pipeline QA batch gồm:
- Retrieval (Chroma + embedding model)  
- Rerank (BAAI/bge-reranker-v2-m3)  
- Sinh câu trả lời (OpenAI: gpt-4o-mini)  

---

### 4.1. Retrieval

Input là:
- Câu hỏi đầy đủ + 4 lựa chọn A/B/C/D  

Query được embed và tìm `top_k` chunks trong Chroma.

`collection.query` trả về:
- distances  
- metadatas  
- documents  

Distance dùng để lọc sơ bộ.

---

### 4.2. Rerank

Reranker đánh giá lại cặp `(query, chunk)` và sắp xếp theo score giảm dần.  
Chỉ lấy `rerank_top_k` chunks để làm context cuối.

→ Reranker cần thiết vì embedding retrieval có thể trả về chunk “gần chủ đề” nhưng không đúng câu hỏi.

---