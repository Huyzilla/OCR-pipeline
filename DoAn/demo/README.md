# RAG PDF Demo

Demo Streamlit cho hỏi đáp tự do trên PDF.

## Chạy

```powershell
powershell -ExecutionPolicy Bypass -File .\demo\run_demo.ps1
```

Hoặc chạy thủ công:

```powershell
conda activate huy
python -m streamlit run demo/frontend/app.py --server.fileWatcherType none
```

## Cấu trúc

```text
demo/
|-- backend/      # OCR, document check, retrieval, routing, LLM service
|-- frontend/     # Streamlit UI
`-- runtime/      # File upload/OCR/chunk tạm, được ignore khỏi git
```

## Luồng

- `Corpus QA`: hỏi trên corpus OCR sẵn.
- `Upload Document QA`: upload PDF, check OCR sẵn; nếu chưa có thì OCR + chunk rồi mới cho hỏi.
