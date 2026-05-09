# PROJECT_STRUCTURE

Mục tiêu: file này là bản đồ nhánh của project để tra cứu context, hạn chế việc quét lại toàn bộ thư mục.

## 1) Tổng quan pipeline

Luồng chính:
1. `crop_header.py` -> cắt header PDF
2. `ocr.py` -> OCR ra `outputs/PublicXXX/main.md`
3. `chunking.py` hoặc `main_chunking.py` -> tạo `chunks_output_finals/PublicXXX/main_chunks_viettel.json`
4. `indexing.py` -> tạo/chạy index truy hồi
5. `test.py` hoặc `run_qa_evaluation.py` -> infer QA
6. `ragas_eval.py` -> chấm chất lượng RAG

## 2) Các thư mục và file quan trọng

- `README.md`
  - Hướng dẫn chạy tổng hợp.

- `crop_header.py`
  - Tiền xử lý PDF trước OCR.

- `ocr.py`
  - OCR từ PDF đã crop, xuất markdown + images.

- `post_processing.py`
  - Hậu xử lý markdown sau OCR.

- `chunking.py`
  - Table-aware chunking (text + table), output JSON chunks.

- `main_chunking.py`
  - Batch chunking cho nhiều thư mục `outputs/PublicXXX`.

- `indexing.py`
  - Tạo index truy hồi từ chunks.

- `qa/`
  - `retrieval.py`: hybrid retrieval + rerank logic.
  - `llm.py`: gọi model trả lời.
  - `pipeline.py`: orchestration QA.
  - `utils.py`: helper dùng chung.
  - `tracing.py`: trace/telemetry.

- `run_qa_evaluation.py`
  - Entry point QA pipeline (version `qa/`).

- `test.py`
  - Batch QA với Chroma + reranker + OpenAI.
  - Có xuất context mỗi câu ra JSON để debug/eval.

- `ragas_eval.py`
  - Chấm điểm RAGAS từ file context JSON của `test.py`.

- `question.csv`
  - Bộ câu hỏi đầu vào.

- `ans.md`, `truth.md`
  - Đáp án đối chiếu.

## 3) Dữ liệu trung gian/kết quả

- `outputs/`
  - OCR output theo từng tài liệu: `outputs/PublicXXX/main.md`

- `chunks_output_finals/`
  - Chunk JSON theo từng tài liệu: `chunks_output_finals/PublicXXX/main_chunks_viettel.json`

- `chroma_db_viettel/`
  - Persistent ChromaDB cho retrieval.

- `task2_batch_output_10.csv`, `task2_batch_output_10_contexts.json`
  - Kết quả trả lời và context đã gửi cho LLM.

- `ragas_scores_10.csv`, `ragas_scores_10.json`
  - Kết quả đánh giá RAGAS.

## 4) Lệnh chạy nhanh thông dụng

- Test 10 câu bằng `test.py`:
  ```bash
  python test.py --question_csv question.csv --chroma_path chroma_db_viettel --collection_name rag_viettel --output task2_batch_output_10.csv --limit 10 --top_k 10 --rerank_top_k 5 --openai_model gpt-4o

- Chấm RAGAS từ context log:
  python ragas_eval.py --input_json task2_batch_output_10_contexts.json --output_json ragas_scores_10.json --output_csv ragas_scores_10.csv --openai_model gpt-4o --embedding_model text-embedding-3-small

## 5) Quy ước để tra cứu nhanh khi hỗ trợ 

Khi nhận request mới, ưu tiên đọc theo thứ tự 
1. PROJECT_STRUCTURE.md (file này)
2. README.md
3. File script liên quan trực tiếp request (vd: test.py, chunking.py, indexing.py)

Chỉ quét rộng toàn bộ project khi:
- Có thay đổi cấu trúc thư mục 
- User báo lỗi không rõ nằm ở đâu 
- Cần tìm symbol/hàm mà file map này không đề cập 

## 6) Cập nhật file này khi nào

Cập nhật PROJECT_STRUCTURE.md ngay khi có thay đổi:
- Tên thư mục kết quả (vd chunks_output_finals)
- File entrypoint chính 
- Pipeline retrieval/QA/eval
- Tên model default quan trọng 

Last updated: 2026-04-12
