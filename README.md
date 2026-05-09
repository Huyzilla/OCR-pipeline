# OCR Pipeline

## Cấu trúc thư mục

```
├── run_ocr.py              # Entry point: PDF → markdown (crop + OCR + post-process per file)
├── run_rag.py              # Entry point: markdown → chunks → ChromaDB
├── run_qa_evaluation.py    # Entry point: QA evaluation
│
├── ocr/                    # Module OCR
│   ├── crop_header.py      # Crop header table từ PDF
│   ├── ocr.py              # Marker PDF→markdown converter
│   └── post_processing.py  # Normalize markdown headings/lists
│
├── rag/                    # Module RAG
│   ├── chunking.py         # TableAwareChunker
│   ├── main_chunking.py    # CLI chunking wrapper
│   └── indexing.py         # Index chunks vào ChromaDB
│
├── qa/                     # Module QA
│   ├── retrieval.py        # HybridQAPipeline (BM25 + dense + rerank)
│   ├── llm.py              # QwenAnswerer
│   ├── pipeline.py         # Orchestration
│   ├── tracing.py          # OpikTracer
│   └── utils.py            # Tiện ích dùng chung
│
├── outputs/                # Output markdown từ OCR
├── chunk_outputs_finals/   # Output chunks JSON
└── chroma_db_viettel/      # ChromaDB vector store
```

## 1) Chuẩn bị môi trường

```powershell
conda activate your_env
pip install -r requirements.txt
```

## 2) OCR Pipeline — `run_ocr.py`

Mỗi file PDF sẽ tự động đi qua toàn bộ pipeline: **crop header → OCR (marker) → post-process** rồi lưu vào `outputs/` trước khi sang file tiếp theo. Có resume mode (bỏ qua file đã có output).

### Chạy cả thư mục

```powershell
python run_ocr.py --input_dir path/to/pdfs --output_dir outputs
```

### Chạy 1 file

```powershell
python run_ocr.py --input_pdf Public283.pdf --output_dir outputs
```

### Tùy chọn

| Flag | Mặc định | Mô tả |
|------|----------|-------|
| `--output_dir` | `outputs` | Thư mục lưu kết quả |
| `--table_format` | `html` | Format bảng: `html` hoặc `markdown` |
| `--buffer_ratio` | `0.005` | Buffer ratio cho crop header |
| `--fallback_ratio` | `0.10` | Fallback ratio khi không detect table |

### Cấu trúc output

```
outputs/
  Public283/
    main.md
    images/
```

## 3) RAG Pipeline — `run_rag.py`

Một lệnh duy nhất để **chunking → indexing** vào ChromaDB.

### Chạy đầy đủ (chunking + indexing)

```powershell
python run_rag.py --input_dir outputs --chunk_dir chunk_outputs_finals --chroma_path chroma_db_viettel --reset_collection
```

### Chỉ chunking (bỏ indexing)

```powershell
python run_rag.py --input_dir outputs --chunk_dir chunk_outputs_finals --skip_indexing
```

### Chỉ indexing (đã có chunks)

```powershell
python run_rag.py --skip_chunking --chunk_dir chunk_outputs_finals --chroma_path chroma_db_viettel --reset_collection
```

### Tùy chọn

| Flag | Mặc định | Mô tả |
|------|----------|-------|
| `--input_dir` | `outputs` | Thư mục markdown |
| `--chunk_dir` | `chunk_outputs_finals` | Thư mục lưu chunk JSON |
| `--chroma_path` | `./chroma_db_viettel` | Đường dẫn ChromaDB |
| `--collection_name` | `rag` | Tên collection |
| `--batch_size` | `256` | Batch size khi indexing |
| `--id_prefix` | `viettel_v1` | Prefix ID |
| `--reset_collection` | | Xóa collection cũ trước khi index |
| `--config` | | Config JSON cho chunking |
| `--skip_chunking` | | Bỏ qua bước chunking |
| `--skip_indexing` | | Bỏ qua bước indexing |

## 4) Cấu trúc QA

Phần QA:

- `qa/utils.py`: các hàm tiện ích dùng chung, load chunk, detect `Publicxxx`, so sánh kết quả với truth
- `qa/retrieval.py`: `HybridQAPipeline` với BM25 + dense + rerank + cache + mở rộng ngữ cảnh theo `prev_chunk_id/next_chunk_id`
- `qa/llm.py`: `QwenAnswerer` để gọi Qwen2.5-3B-Instruct
- `qa/tracing.py`: `OpikTracer` để trace prompt/context/output
- `qa/pipeline.py`: orchestration chính của luồng infer
- `run_qa_evaluation.py`: entrypoint CLI, chỉ parse args rồi gọi pipeline

## 5) QA Evaluation — `run_qa_evaluation.py`

Script `run_qa_evaluation.py` dùng hybrid retrieval + rerank + Qwen để trả lời trắc nghiệm và xuất kết quả theo format:
- `1,B`
- `2,"A,B"`

Mặc định script sẽ:
- Tự load `.env`
- Dùng cache `.qa_cache/` để không encode lại mỗi lần chạy
- Route theo `Publicxxx` nếu câu hỏi có nhắc tới tài liệu cụ thể, ngược lại fallback global
- Mở rộng context retrieval theo chunk liền kề (`prev_chunk_id`, `next_chunk_id`) với `--neighbor_hops 1`

### Chạy infer 100 câu đầu (khuyến nghị để test nhanh)

```powershell
python run_qa_evaluation.py --question_csv question.csv --chunk_dir chunks_output_finals --output result.md --max_questions 100
```

### Chạy test 10 câu đầu

```powershell
python test.py --question_csv question.csv --chroma_path chroma_db_viettel --collection_name rag_viettel --output task2_batch_output_10.csv --limit 10 --top_k 10 --rerank_top_k 5 --openai_model gpt-4o-mini
```

### Chạy full file question.csv

```powershell
python run_qa_evaluation.py --question_csv question.csv --chunk_dir chunks_output_finals --output result.md --max_questions 0
```

### Tùy chọn khi infer

- Dùng Qwen (mặc định):

```powershell
python run_qa_evaluation.py --question_csv question.csv --chunk_dir chunks_output_finals --output result.md --max_questions 100 --llm_model Qwen/Qwen2.5-3B-Instruct
```

- Tắt LLM, chỉ dùng retrieval + scoring:

```powershell
python run_qa_evaluation.py --question_csv question.csv --chunk_dir chunks_output_finals --output result.md --max_questions 100 --disable_llm
```

- Bật Opik trace để xem prompt/context/output:

```powershell
python run_qa_evaluation.py --question_csv question.csv --chunk_dir chunks_output_finals --output huy.md --max_questions 10 --llm_model Qwen/Qwen2.5-3B-Instruct --opik_trace --opik_project ocr-pipeline-qa
```

- Opik test nhanh 10 câu (kèm neighbor retrieval):

```powershell
python run_qa_evaluation.py --question_csv question.csv --chunk_dir chunks_output_finals --output result_opik_10.md --max_questions 10 --llm_model Qwen/Qwen2.5-3B-Instruct --neighbor_hops 1 --opik_trace --opik_project ocr-pipeline-qa
```

- So sánh với file truth và xuất câu lệch:

```powershell
python run_qa_evaluation.py --question_csv question.csv --chunk_dir chunks_output_finals --output result.md --max_questions 100 --truth_file truth.md --mismatch_output mismatch_vs_truth.md
```

### Các cờ hữu ích khác

- `--cache_dir .qa_cache`: đổi thư mục cache retrieval
- `--no_cache`: tắt cache và rebuild lại BM25/dense
- `--opik_use_local`: dùng Opik local backend
- `--llm_max_new_tokens`: giới hạn độ dài output của model
- `--neighbor_hops`: số hop mở rộng theo `prev_chunk_id/next_chunk_id` (0 để tắt)
