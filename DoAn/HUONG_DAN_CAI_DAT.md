# Hướng dẫn cài đặt và chạy

## 1. Yêu cầu môi trường

- Python 3.10 hoặc 3.11.
- Khuyến nghị dùng Conda/Miniconda.
- Cần `OPENAI_API_KEY` nếu chạy các chức năng dùng GPT để định tuyến hoặc sinh câu trả lời.

## 2. Tạo môi trường

```powershell
conda create -n doan python=3.10 -y
conda activate doan
pip install -r requirements.txt
```

Nếu đã có môi trường `huy` như trong quá trình phát triển:

```powershell
conda activate huy
pip install -r requirements.txt
```

## 3. Cấu hình API key

Sao chép file `.env.example` thành `.env`, sau đó điền khóa API:

```powershell
Copy-Item .env.example .env
```

Nội dung tối thiểu:

```text
OPENAI_API_KEY=your_api_key_here
```

Không nộp hoặc chia sẻ file `.env` thật vì file này chứa khóa bí mật.

## 4. Chạy demo Streamlit

Từ thư mục gốc của gói nộp:

```powershell
powershell -ExecutionPolicy Bypass -File .\demo\run_demo.ps1
```

Hoặc chạy thủ công:

```powershell
python -m streamlit run demo/frontend/app.py --server.fileWatcherType none
```

Trong giao diện demo:

- `Corpus QA`: hỏi đáp trên corpus/chunk có sẵn.
- `Upload Document QA`: tải PDF lên, hệ thống OCR/chunk nếu cần rồi trả lời câu hỏi.
- Để chạy nhẹ và không cần checkpoint cục bộ, chọn `BM25-only nhanh`, `Không rerank`, router mặc định hoặc GPT-4o mini.
- Các lựa chọn model fine-tune cục bộ cần bổ sung checkpoint vào thư mục `models/`.

## 5. Chạy các script chính

Baseline router:

```powershell
python scripts/run_baseline_router.py
```

Router-summary:

```powershell
python scripts/run_router_summary.py
```

OCR tài liệu PDF:

```powershell
python scripts/run_ocr.py --input_dir path/to/pdfs --output_dir outputs
```

Chunking và indexing:

```powershell
python scripts/run_rag.py --input_dir outputs --chunk_dir chunk_outputs_finals --chroma_path chroma_db_viettel --reset_collection
```

## 6. Ghi chú về dung lượng gói nộp

Gói nộp không bao gồm:

- Checkpoint/model cục bộ trong `models/`.
- Cache embedding trong `cache/`.
- Dataset lớn như `mmarco_vi_50k.jsonl`, `mmarco_vi_100k.jsonl`.
- Artifact thực nghiệm lớn trong `domain_data/`.

Các thành phần này có thể được tải/tạo lại khi cần. Việc lược bỏ giúp file `.zip` đáp ứng giới hạn dung lượng 30MB.
