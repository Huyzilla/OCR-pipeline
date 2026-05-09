# QA Pipeline - Hướng dẫn Chi Tiết

## 📋 Tóm tắt

Đây là một pipeline hoàn chỉnh để chạy QA (Question Answering) trên các context đã được fusion sử dụng:
- **LLM**: Qwen/Qwen2.5-3B-Instruct
- **Dữ liệu**: Fused contexts từ `task2_batch_output_fused_contexts_v2.json`

## 🎯 Các File Chính

| File | Mô tả |
|------|--------|
| `run_qa_with_fused_contexts.py` | Full QA pipeline (default) |
| `run_qa_lightweight.py` | Version nhẹ với 8-bit quantization |
| `check_environment.py` | Kiểm tra environment |
| `analyze_qa_results.py` | Phân tích kết quả |
| `config_qa.py` | Cấu hình (có thể tùy chỉnh) |
| `run.sh` | Interactive quick-start script |

## ⚙️ Cài Đặt

### Bước 1: Cài đặt Dependencies

```bash
# Option 1: Từ requirements file
pip install -r requirements_qa.txt

# Option 2: Manual install
pip install torch transformers tqdm pandas bitsandbytes accelerate

# Option 3: Với GPU support (CUDA 11.8)
pip install torch --index-url https://download.pytorch.org/whl/cu118
pip install transformers tqdm pandas
```

### Bước 2: Kiểm tra Environment

```bash
python3 check_environment.py
```

Output sẽ hiển thị:
- ✓ Files check
- ✓ Dependencies check
- ✓ GPU/CUDA info
- ✓ Estimated runtime

## 🚀 Sử Dụng

### Cách 1: Interactive Mode (Dễ nhất)

```bash
bash run.sh
```

Chọn một trong 4 tùy chọn:
1. Full pipeline (tất cả questions)
2. Lightweight mode (tối ưu memory)
3. Test mode (10 questions)
4. Analyze results

### Cách 2: Command Line Direct

#### Quick start (default settings)
```bash
python3 run_qa_with_fused_contexts.py
```

#### Lightweight mode (GPU memory < 12GB)
```bash
python3 run_qa_lightweight.py
```

#### Test 10 questions
```bash
python3 run_qa_lightweight.py --limit 10 --output test_results.json
```

#### Custom settings
```bash
python3 run_qa_with_fused_contexts.py \
  --model Qwen/Qwen2.5-3B-Instruct \
  --max-tokens 256 \
  --output-json my_results.json
```

### Cách 3: Từ Python Code

```python
from run_qa_with_fused_contexts import (
    initialize_model, load_fused_contexts, 
    load_questions, run_qa_pipeline
)

# Load data
contexts = load_fused_contexts('task2_batch_output_fused_contexts_v2.json')
questions = load_questions('question.csv')

# Initialize model
tokenizer, model, device = initialize_model('Qwen/Qwen2.5-3B-Instruct')

# Run
results = run_qa_pipeline(tokenizer, model, device, contexts, questions)

# Use results...
```

## 📊 Phân Tích Kết Quả

### Analyze results
```bash
python3 analyze_qa_results.py analyze qa_results_with_fused_contexts.json
```

Output:
```
📊 Basic Statistics:
  Total questions processed: 100
📝 Answer Statistics:
  Min length: 10 chars
  Max length: 256 chars
  Avg length: 89.5 chars
📚 Context Statistics:
  Min tokens: 122
  Max tokens: 608
  Avg tokens: 354.2
```

### Convert JSON to CSV
```bash
python3 analyze_qa_results.py convert qa_results_with_fused_contexts.json results.csv
```

### Extract answers only
```bash
python3 analyze_qa_results.py extract qa_results_with_fused_contexts.json -o answers.json
```

### Compare two result files
```bash
python3 analyze_qa_results.py compare results1.json results2.json
```

## 🔧 Tùy Chỉnh Cấu Hình

### Chỉnh sửa `config_qa.py`:

```python
# Change model
LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"

# Change output tokens
MAX_NEW_TOKENS = 512

# Enable 8-bit quantization
USE_8BIT = True

# Adjust generation parameters
TEMPERATURE = 0.5  # More deterministic
TOP_P = 0.95
```

### Command-line overrides:

```bash
python3 run_qa_with_fused_contexts.py \
  --model mistralai/Mistral-7B-Instruct-v0.1 \
  --max-tokens 512
```

## 📈 Performance Tuning

### Giảm Memory Usage

```bash
# 8-bit quantization
python3 run_qa_lightweight.py

# Hoặc explicit
python3 run_qa_with_fused_contexts.py \
  --output qa_results.json
# Sửa config_qa.py: USE_8BIT = True
```

### Tăng Tốc Độ

```bash
# Giảm output tokens
python3 run_qa_with_fused_contexts.py --max-tokens 128

# Dùng GPU (automatic)
# Hoặc: CUDA_VISIBLE_DEVICES=0 python3 run_qa_with_fused_contexts.py
```

### Xử Lý Batch (nếu modify code)

```python
# In run_qa_with_fused_contexts.py
BATCH_SIZE = 4  # Process 4 at a time
# Sửa run_qa_pipeline() để batch
```

## 🐛 Troubleshooting

### CUDA Out of Memory

**Problem**: `RuntimeError: CUDA out of memory`

**Solution**:
```bash
# Use lightweight mode with 8-bit
python3 run_qa_lightweight.py

# Or reduce tokens
python3 run_qa_with_fused_contexts.py --max-tokens 128

# Or use CPU
CUDA_VISIBLE_DEVICES="" python3 run_qa_with_fused_contexts.py
```

### Model Download Error

**Problem**: Model không download được

**Solution**:
```bash
# Pre-download model
python3 -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-3B-Instruct')"

# Check HuggingFace token
huggingface-cli login
```

### Empty Answers

**Problem**: Kết quả trả về câu trả lời rỗng

**Solution**:
```bash
# Increase max tokens
python3 run_qa_with_fused_contexts.py --max-tokens 256

# Change temperature
# Sửa config_qa.py: TEMPERATURE = 0.5
```

### Slow Performance

**Problem**: Chạy rất chậm

**Solution**:
```bash
# Check if using GPU
python3 check_environment.py

# If CPU, try GPU version
CUDA_VISIBLE_DEVICES=0 python3 run_qa_with_fused_contexts.py

# Or reduce questions
python3 run_qa_lightweight.py --limit 10
```

## 📊 Output Format

### JSON Output
```json
{
  "question_index": 0,
  "question": "Trong mô hình nhà thông minh, IoT chủ yếu đóng vai trò gì?",
  "llm_context": "Trong mô hình nhà thông minh, IoT...",
  "answer": "Kết nối Internet và quản lý thiết bị từ xa",
  "context_token_count": 388,
  "fusion_time": 5.04,
  "options": [
    "Lưu trữ dữ liệu trên máy chủ",
    "Kết nối Internet và quản lý thiết bị từ xa",
    "Cung cấp dịch vụ phân tích dữ liệu lớn",
    "Thay thế hoàn toàn điện toán đám mây"
  ]
}
```

### CSV Output
```csv
question_index,question,answer,context_token_count,fusion_time,option_A,option_B,...
0,Trong mô hình...,Kết nối Internet...,388,5.04,Lưu trữ dữ liệu,...,...
```

## 📝 Example Workflows

### Workflow 1: Quick Test
```bash
# 1. Check environment
python3 check_environment.py

# 2. Test with 10 questions
python3 run_qa_lightweight.py --limit 10 --output test.json

# 3. Analyze results
python3 analyze_qa_results.py analyze test.json
```

### Workflow 2: Full Run with Analysis
```bash
# 1. Full pipeline
python3 run_qa_with_fused_contexts.py

# 2. Analyze
python3 analyze_qa_results.py analyze qa_results_with_fused_contexts.json

# 3. Convert to CSV
python3 analyze_qa_results.py convert qa_results_with_fused_contexts.json results.csv

# 4. Extract answers
python3 analyze_qa_results.py extract qa_results_with_fused_contexts.json -o answers.json
```

### Workflow 3: Memory-Constrained Environment
```bash
# 1. Use lightweight with 8-bit
python3 run_qa_lightweight.py

# 2. Reduce tokens if needed
# Sửa config_qa.py: MAX_NEW_TOKENS = 128

# 3. Run again
python3 run_qa_lightweight.py

# 4. Analyze
python3 analyze_qa_results.py analyze qa_results_lightweight.json
```

## 🔬 Monitoring & Logging

### Enable detailed logging
```bash
# Add logging in check_environment.py
python3 -u check_environment.py  # Unbuffered output

# Monitor GPU during run
# Terminal 1:
python3 run_qa_with_fused_contexts.py

# Terminal 2:
watch -n 1 nvidia-smi
```

### Performance profiling
```python
import time
start = time.time()
results = run_qa_pipeline(...)
elapsed = time.time() - start
print(f"Total time: {elapsed:.2f}s")
print(f"Per question: {elapsed/len(results):.2f}s")
```

## 💾 Data Management

### Backup results
```bash
cp qa_results_with_fused_contexts.json qa_results_backup_$(date +%Y%m%d).json
```

### Archive multiple runs
```bash
# Create comparison
mkdir qa_runs
python3 run_qa_with_fused_contexts.py
mv qa_results_*.* qa_runs/run_1/

python3 run_qa_lightweight.py
mv qa_results_*.* qa_runs/run_2/
```

## 🎓 Best Practices

1. **Luôn kiểm tra environment trước**: `python3 check_environment.py`
2. **Test với vài questions trước**: `--limit 10`
3. **Backup kết quả**: Tự động hoặc manual
4. **Monitor GPU/RAM**: Dùng `watch nvidia-smi` (GPU)
5. **Adjust parameters**: Temperature, tokens, batch size
6. **Validate outputs**: Kiểm tra sample results

## 📞 Support & Tips

- **Slow on CPU**: Use GPU hoặc giảm questions
- **Memory error**: Use lightweight mode hoặc giảm tokens  
- **Long runtime**: Tăng max_tokens có thể làm nó chậm hơn
- **Quality concern**: Adjust temperature (0.3-0.7 tốt hơn)

---

**Phiên bản**: 1.0  
**Cập nhật**: 2024-05-04
