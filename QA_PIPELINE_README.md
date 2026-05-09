# QA Pipeline với Fused Contexts

## Mô tả

Script này chạy QA (Question Answering) với các context đã được fusion, sử dụng:
- **LLM**: Qwen/Qwen2.5-3B-Instruct
- **Embedding model**: AITeamVN/Vietnamese_Embedding_v2
- **Input**: Fused contexts từ `task2_batch_output_fused_contexts_v2.json`

## Yêu cầu

### Hardware
- **GPU** (khuyến nghị): RTX 3060/3080+ với ít nhất 8GB VRAM
- **CPU**: Có thể chạy trên CPU nhưng rất chậm

### Software
- Python 3.8+
- PyTorch 2.0+
- Transformers 4.30+
- CUDA Toolkit 11.8+ (nếu dùng GPU)

## Cài đặt

### 1. Cài đặt dependencies

```bash
pip install torch transformers tqdm pandas cuda-toolkit
```

Hoặc cài PyTorch phiên bản GPU:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. Kiểm tra môi trường

```bash
python check_environment.py
```

Output sẽ check:
- ✓ Files required
- ✓ Dependencies
- ✓ GPU availability
- ✓ Data validation
- ℹ Estimated runtime

## Sử dụng

### Quick Start

```bash
python run_qa_with_fused_contexts.py
```

### Advanced Options

```bash
python run_qa_with_fused_contexts.py \
  --model Qwen/Qwen2.5-3B-Instruct \
  --fused-contexts task2_batch_output_fused_contexts_v2.json \
  --questions question.csv \
  --output-json qa_results_with_fused_contexts.json \
  --output-csv qa_results_with_fused_contexts.csv \
  --max-tokens 256
```

## Tham số

| Tham số | Mặc định | Mô tả |
|---------|----------|--------|
| `--model` | `Qwen/Qwen2.5-3B-Instruct` | Model LLM cần dùng |
| `--fused-contexts` | `task2_batch_output_fused_contexts_v2.json` | File chứa fused contexts |
| `--questions` | `question.csv` | File chứa questions |
| `--output-json` | `qa_results_with_fused_contexts.json` | Output JSON file |
| `--output-csv` | `qa_results_with_fused_contexts.csv` | Output CSV file |
| `--max-tokens` | `256` | Max tokens để generate answer |

## Output

### JSON Format
```json
{
  "question_index": 0,
  "question": "Trong mô hình nhà thông minh, IoT chủ yếu đóng vai trò gì?",
  "context_token_count": 388,
  "fusion_time": 5.04,
  "answer": "Kết nối Internet và quản lý thiết bị từ xa",
  "options": ["Lưu trữ dữ liệu trên máy chủ", "Kết nối Internet và quản lý thiết bị từ xa", ...],
  "timestamp": "2024-05-04T10:30:45.123456"
}
```

### CSV Format
```csv
question_index,question,answer,context_token_count,fusion_time,option_A,option_B,option_C,option_D
0,Trong mô hình nhà thông minh...,Kết nối Internet và quản lý thiết bị từ xa,388,5.04,Lưu trữ dữ liệu...,Kết nối Internet...,...
```

## Cấu trúc Input

### Fused Contexts (`task2_batch_output_fused_contexts_v2.json`)
```json
[
  {
    "question_index": 0,
    "question": "Câu hỏi 1",
    "llm_context": "Context được fusion từ các tài liệu...",
    "fusion_time": 5.04,
    "context_token_count": 388
  },
  ...
]
```

### Questions (`question.csv`)
```csv
Question,A,B,C,D
"Câu hỏi 1","Đáp án A","Đáp án B","Đáp án C","Đáp án D"
...
```

## Prompting Strategy

Prompt được tạo theo format:
```
Dựa vào thông tin sau đây, vui lòng trả lời câu hỏi.

CONTEXT:
[fused context]

QUESTION:
[question]

OPTIONS:
A. [option_a]
B. [option_b]
C. [option_c]
D. [option_d]

ANSWER:
```

## Optimization Tips

### Giảm memory usage
- Sử dụng `--max-tokens 128` thay vì 256
- Có thể load model với `torch_dtype=torch.float8`

### Tăng tốc độ
- Sử dụng GPU (nếu có)
- Batch processing (modify script)
- Model quantization

### Tùy chỉnh generation parameters
Chỉnh sửa trong `run_qa_with_fused_contexts.py`:
```python
TEMPERATURE = 0.7  # Thấp hơn = deterministic, cao hơn = creative
TOP_P = 0.9        # Nucleus sampling
MAX_NEW_TOKENS = 256
```

## Troubleshooting

### CUDA Out of Memory
```bash
# Giảm max tokens
python run_qa_with_fused_contexts.py --max-tokens 128

# Hoặc dùng CPU
CUDA_VISIBLE_DEVICES="" python run_qa_with_fused_contexts.py
```

### Model download slow
Model sẽ được download tự động lần đầu tiên. Để download trước:
```bash
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-3B-Instruct')"
```

### Memory error on CPU
- Tắt các chương trình khác
- Tăng swap memory
- Sử dụng CPU quantization

## Performance

### Estimated Time
- **GPU (RTX 3080)**: ~30-45 phút cho 100 questions
- **GPU (RTX 3060)**: ~45-60 phút cho 100 questions  
- **CPU (Intel i7)**: ~4-6 giờ cho 100 questions

### Memory Requirements
- **GPU**: 8GB+ (tùy model size)
- **CPU**: 16GB+ (khuyến nghị)

## Example Usage

```bash
# 1. Kiểm tra môi trường
python check_environment.py

# 2. Nếu OK, chạy pipeline
python run_qa_with_fused_contexts.py

# 3. Xem kết quả
# - qa_results_with_fused_contexts.json (full details)
# - qa_results_with_fused_contexts.csv (spreadsheet format)
```

## Output Analysis

Sau khi chạy, có thể phân tích kết quả:

```python
import json
import pandas as pd

# Load JSON results
with open('qa_results_with_fused_contexts.json') as f:
    results = json.load(f)

# Load CSV for easy analysis
df = pd.read_csv('qa_results_with_fused_contexts.csv')

# Statistics
print(f"Total questions: {len(results)}")
print(f"Avg context tokens: {df['context_token_count'].mean():.0f}")
print(f"Total fusion time: {df['fusion_time'].sum():.2f}s")
print(f"Avg answer length: {df['answer'].str.len().mean():.0f} chars")
```

## Lưu ý

1. **Lần đầu chạy** sẽ download model Qwen2.5-3B-Instruct (~6GB)
2. **Thời gian chạy** phụ thuộc vào số lượng questions và hardware
3. **Memory usage** có thể cao nếu context lớn
4. **Quality** của answer phụ thuộc vào chất lượng fused contexts

## Support

Nếu gặp vấn đề:
1. Kiểm tra `check_environment.py` output
2. Xem error message chi tiết
3. Kiểm tra file input format
4. Thử reduced settings (--max-tokens, smaller model)

---

**Last updated**: 2024-05-04
