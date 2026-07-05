# Dự Án RAG QA Tiếng Việt

Repository này chứa pipeline RAG tiếng Việt phục vụ OCR tài liệu, chia chunk,
đánh chỉ mục, truy hồi, rerank, định tuyến câu hỏi, sinh câu trả lời, đo đạc
latency/benchmark và viết báo cáo đồ án.

## Môi Trường

Trước khi chạy bất kỳ script nào, kích hoạt môi trường conda:

```powershell
conda activate huy
```

Cài dependency nếu cần:

```powershell
pip install -r requirements.txt
```

Tạo file `.env` từ `.env.example` và điền các API key cần thiết.

## Cấu Trúc Thư Mục

```text
DATN_backup/
|-- configs/                  # File cấu hình mẫu
|-- scripts/                  # Script chạy chính và script hỗ trợ
|-- src/                      # Mã nguồn có thể import
|   |-- rag/                  # Chunking và indexing
|   |-- qa/                   # Đọc câu hỏi, ghi output, OpenAI helper, utils
|   |-- ocr/                  # Xử lý OCR PDF
|   |-- baseline_fusion/      # Logic retrieval/prompt/output cho baseline
|   `-- pipeline_router_summary/
|-- training/
|   `-- data_preparation_pipeline/
|       |-- data_embedding/   # Chuẩn bị dữ liệu huấn luyện embedding
|       |-- data_reranker/    # Chuẩn bị dữ liệu huấn luyện reranker
|       `-- tools/            # Tiện ích một lần: mMARCO, Voyage, map gold corpus
|-- models/                   # Model/checkpoint/cache cục bộ
|-- data/                     # Dữ liệu QA/evaluation gốc
|-- domain_data/              # Artifact đánh giá theo miền
|-- chunk_outputs_finals/     # Chunk JSON đã sinh
|-- doc_index/                # Document index cho router-summary
|-- cache/                    # Cache runtime
|-- logs/                     # Log cục bộ
|-- tests/                    # Test
`-- GOAL/                     # Báo cáo đồ án, tách riêng khỏi code
```

Các model/checkpoint cục bộ được gom trong `models/`, ví dụ:

```text
models/
|-- embed_gist_mnr/
|-- MiniLM_H384_pruned_ft/
|-- sbert_routing/
`-- hf_cache/
```

## Ba Script Chạy Chính

Baseline dùng GPT-4o-mini làm router:

```powershell
python scripts/run_baseline_router.py
```

Router-summary:

```powershell
python scripts/run_router_summary.py
```

Baseline GIST + MiniLM, dùng `models/sbert_routing/` làm router thay vì GPT-4o-mini:

```powershell
python scripts/run_baseline_gist_minilm.py
```

## Đo Đạc

Các file `measure_*` cũ đã được gộp vào một script:

```powershell
python scripts/measure.py router-summary --n 20 --mode cached
python scripts/measure.py router-summary --n 20 --mode detailed
python scripts/measure.py baseline-router --n 20
python scripts/measure.py reranker --n 20 --models bge,minilm,phoranker
```

Nếu chỉ muốn đo PhoRanker và dùng lại cache candidate pairs:

```powershell
python scripts/measure.py reranker --models phoranker
```

## Pipeline OCR/RAG Dữ Liệu

Chạy OCR:

```powershell
python scripts/run_ocr.py --input_dir path/to/pdfs --output_dir outputs
```

Chạy chunking và indexing:

```powershell
python scripts/run_rag.py --input_dir outputs --chunk_dir chunk_outputs_finals --chroma_path chroma_db_viettel --reset_collection
```

Chỉ chạy chunking:

```powershell
python scripts/run_rag.py --input_dir outputs --chunk_dir chunk_outputs_finals --skip_indexing
```

Chỉ chạy indexing:

```powershell
python scripts/run_rag.py --skip_chunking --chunk_dir chunk_outputs_finals --chroma_path chroma_db_viettel --reset_collection
```

## Pipeline Chuẩn Bị Dữ Liệu Huấn Luyện

Pipeline dữ liệu reranker:

```powershell
python training/data_preparation_pipeline/data_reranker/run_pipeline.py status
python training/data_preparation_pipeline/data_reranker/run_pipeline.py all --dry-run --smoke-n 1
```

Pipeline dữ liệu embedding:

```powershell
python training/data_preparation_pipeline/data_embedding/module2_build_master.py
python training/data_preparation_pipeline/data_embedding/module3_split.py
```

## Ghi Chú

- Logic helper cho baseline nằm trong `src/baseline_fusion/runner.py`.
- Logic helper cho router-summary nằm trong `src/pipeline_router_summary/runner.py`.
- Các script trong `scripts/` dùng `scripts/_bootstrap.py` để thêm `src/` vào
  `sys.path`, nên các import như `from qa...` và `from rag...` vẫn chạy được khi
  gọi script từ thư mục gốc repository.
- `GOAL/` là phần báo cáo đồ án, không nằm trong runtime pipeline.
- `models/` chứa checkpoint/cache cục bộ và được ignore khỏi git.
