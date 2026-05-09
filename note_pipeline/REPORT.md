# REPORT: OCR + RAG Pipeline (Updated 2026-04-30)

## 1. Tổng quan hiện trạng

Pipeline hiện tại gồm 3 khối chính:

1. OCR: `run_ocr.py` (crop header -> OCR -> post-process markdown)
2. RAG: `run_rag.py` (chunking -> indexing ChromaDB)
3. QA: `test.py` (retrieve -> hybrid rank BM25+dense -> rerank -> LLM)

Luồng dữ liệu:

`PDF -> outputs/PublicXXX/main.md -> chunk_outputs_finals/...json -> chroma_db_viettel -> QA output`

## 2. Cập nhật quan trọng so với bản cũ

### 2.1. Embedding model đã đổi

- Mặc định hiện tại dùng: `AITeamVN/Vietnamese_Embedding_v2`
- Đã đồng bộ trong:
  - `run_rag.py`
  - `test.py`
  - `test_combined_query.py`

### 2.2. Collection Chroma thực tế

- Collection đang tồn tại và được dùng là: `rag`
- Collection `rag_viettel` không tồn tại trong DB hiện tại

### 2.3. `run_rag.py` đã có incremental flow

`run_rag.py` hiện không còn luôn quét/index toàn bộ như trước:

- Chunking chỉ chạy cho `main.md` mới hoặc thay đổi (dựa trên mtime so với file chunk JSON)
- Indexing chỉ upsert các file chunk vừa thay đổi
- Trước khi upsert sẽ xóa chunk cũ theo `document_id` đã thay đổi
- Có fallback tự động khi mismatch embedding dimension:
  - Nếu collection cũ dimension khác model mới, script tự xóa collection và index lại

## 3. Trạng thái metadata trong Chroma hiện tại

Kết quả kiểm tra trực tiếp trên `chroma_db_viettel`:

- Có metadata key:
  - `document_id`
  - `chunk_type`
  - `hierarchy_path`
  - `chunk_index`
  - các key bảng như `raw_html`, `row_start`, `row_end`, `table_id`, ...
- Không có metadata key:
  - `source`
  - `_source`
  - `document_type`
  - `date`

Do đó hiện tại chỉ filter ổn định theo:

- `document_id`
- `chunk_type`

Chưa thể filter theo `source/document_type/date range` nếu chưa bổ sung metadata từ bước chunk/index.

## 4. QA flow hiện tại trong `test.py`

### 4.1. Query và retrieval

1. Tạo query đầy đủ từ `Question + A + B + C + D`
2. Truy hồi dense từ Chroma (`top_k` ứng viên lớn hơn) với optional filter theo `document_id` nếu câu hỏi có `PublicXXX`

### 4.2. Hybrid ranking

3. Trên tập ứng viên retrieve được, tính:
   - điểm vector (từ distance của Chroma, đảo dấu)
   - điểm BM25 (thư viện `rank_bm25`, không phải tự cài BM25 từ đầu)
4. Normalize và trộn theo `hybrid_alpha`

### 4.3. Rerank và answer

5. Rerank bằng CrossEncoder nhưng query chỉ dùng phần câu hỏi (`Question`), không đưa A/B/C/D
6. Build context từ top chunk sau rerank
7. Gọi LLM (`gpt-4o-mini`) để trả lời
8. Parse về format output: `1,B` hoặc `2,"A,B"` hoặc `0,`

## 5. Chroma internals (vì sao có 2 thư mục UUID)

Trong `chroma_db_viettel/` có:

- `chroma.sqlite3` (catalog metadata)
- thư mục UUID cho segment vector HNSW
- thư mục UUID cho segment metadata

Đây là thiết kế bình thường của Chroma, không phải lỗi hay bị nhân đôi DB.

## 6. Khuyến nghị vận hành hiện tại

1. Khi đổi embedding model, nên chạy `run_rag.py` để script tự xử lý dimension mismatch nếu có.
2. Nếu muốn metadata filtering nâng cao (`source`, `document_type`, `date`), cần bổ sung metadata từ bước chunking/indexing trước.
3. Với batch QA dài, tiếp tục dùng chế độ checkpoint/resume trong `test.py` để tránh mất tiến độ.

## 7. Tệp và thư mục chính

- OCR output: `outputs/`
- Chunk JSON: `chunk_outputs_finals/`
- Vector DB: `chroma_db_viettel/`
- QA batch script: `test.py`
- RAG build script: `run_rag.py`

---

Bản REPORT này phản ánh trạng thái code và dữ liệu thực tế tại thời điểm cập nhật.
