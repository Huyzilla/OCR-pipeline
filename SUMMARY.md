# QA Pipeline with Fused Contexts - Summary

## 📦 Created Files

### Main Scripts
1. **run_qa_with_fused_contexts.py** - Full QA pipeline with Qwen2.5-3B
2. **run_qa_lightweight.py** - Lightweight version with 8-bit quantization
3. **check_environment.py** - Environment validation script
4. **analyze_qa_results.py** - Results analysis utility
5. **config_qa.py** - Configuration template

### Documentation
1. **QA_PIPELINE_README.md** - Comprehensive README
2. **USAGE.md** - Detailed usage guide with examples
3. **requirements_qa.txt** - Python dependencies

### Utilities
1. **run.sh** - Interactive quick-start bash script

## 🎯 Quick Start

```bash
# 1. Check environment
python3 check_environment.py

# 2. Run QA pipeline (Choose one)
# Full:
python3 run_qa_with_fused_contexts.py

# Or Lightweight:
python3 run_qa_lightweight.py

# Or Test (10 questions):
python3 run_qa_lightweight.py --limit 10

# 3. Analyze results
python3 analyze_qa_results.py analyze qa_results_with_fused_contexts.json
```

## ⚙️ Features

### Main Pipeline (`run_qa_with_fused_contexts.py`)
- ✅ Full QA with fused contexts
- ✅ Batch processing support
- ✅ JSON & CSV output
- ✅ Progress tracking with tqdm
- ✅ Customizable generation parameters
- ✅ Error handling

### Lightweight Version (`run_qa_lightweight.py`)
- ✅ 8-bit quantization support
- ✅ Memory optimized
- ✅ Faster inference
- ✅ Suitable for <12GB GPU

### Environment Check (`check_environment.py`)
- ✅ File validation
- ✅ Dependency check
- ✅ GPU availability
- ✅ Data alignment
- ✅ Resource estimation

### Results Analysis (`analyze_qa_results.py`)
- ✅ Statistics calculation
- ✅ Result comparison
- ✅ JSON ↔ CSV conversion
- ✅ Answer extraction

## 📊 Pipeline Architecture

```
Input Data
    ↓
[task2_batch_output_fused_contexts_v2.json]
[question.csv]
    ↓
Load & Validate
    ↓
Initialize LLM Model
(Qwen/Qwen2.5-3B-Instruct)
    ↓
For each question:
  1. Get fused context
  2. Create prompt
  3. Generate answer
  4. Save result
    ↓
Output
    ↓
[qa_results_with_fused_contexts.json]
[qa_results_with_fused_contexts.csv]
```

## 🔧 Configuration Options

All available in `config_qa.py`:

```python
# Model
LLM_MODEL = "Qwen/Qwen2.5-3B-Instruct"

# Generation
MAX_NEW_TOKENS = 256
TEMPERATURE = 0.7
TOP_P = 0.9

# I/O
FUSED_CONTEXTS_FILE = "task2_batch_output_fused_contexts_v2.json"
QUESTIONS_CSV_FILE = "question.csv"
OUTPUT_JSON_FILE = "qa_results_with_fused_contexts.json"
OUTPUT_CSV_FILE = "qa_results_with_fused_contexts.csv"

# Optimization
USE_8BIT = False
USE_FLASH_ATTENTION = True
```

## 📈 Performance Estimates

| Hardware | Mode | Speed | Memory |
|----------|------|-------|--------|
| GPU (RTX 3080) | Full | ~30-45 min | 12 GB |
| GPU (RTX 3060) | Full | ~45-60 min | 10 GB |
| GPU (RTX 3060) | Lightweight | ~20-30 min | 8 GB |
| CPU (i7) | CPU only | ~4-6 hours | 16 GB |

## 🚀 Typical Workflow

```
Step 1: Environment Check
├─ Check files exist
├─ Check dependencies
├─ Check GPU availability
└─ Estimate runtime

Step 2: Run QA Pipeline
├─ Load fused contexts
├─ Initialize LLM
├─ Process each question
└─ Save results

Step 3: Analyze Results
├─ Calculate statistics
├─ Convert formats
└─ Extract answers
```

## 💡 Tips & Tricks

### Low GPU Memory (<8GB)
```bash
python3 run_qa_lightweight.py --limit 50
# Process in smaller batches
```

### Need Deterministic Output
```python
# In config_qa.py
TEMPERATURE = 0.3  # Less random
DO_SAMPLE = False   # Greedy decoding
```

### Batch Processing
```bash
# Process 100 questions at a time
for i in {0..4}; do
  python3 run_qa_lightweight.py \
    --limit 100 \
    --output batch_$i.json
done
```

### Compare Different Models
```bash
# Run with different models
python3 run_qa_with_fused_contexts.py \
  --model Qwen/Qwen2.5-3B-Instruct \
  --output results_qwen.json

python3 run_qa_with_fused_contexts.py \
  --model mistralai/Mistral-7B-Instruct-v0.1 \
  --output results_mistral.json

# Compare
python3 analyze_qa_results.py compare results_qwen.json results_mistral.json
```

## 🔍 Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| CUDA Out of Memory | Use `run_qa_lightweight.py` or `--max-tokens 128` |
| Model not found | Pre-download with `huggingface-cli login` |
| Slow performance | Check GPU with `nvidia-smi`, use lighter model |
| Empty answers | Increase `MAX_NEW_TOKENS`, adjust `TEMPERATURE` |

## 📝 Input/Output Examples

### Input: Fused Context
```json
{
  "question_index": 0,
  "question": "Trong mô hình nhà thông minh, IoT chủ yếu đóng vai trò gì?",
  "llm_context": "Trong mô hình nhà thông minh, IoT (Internet of Things)...",
  "fusion_time": 5.04,
  "context_token_count": 388
}
```

### Output: QA Result
```json
{
  "question_index": 0,
  "question": "Trong mô hình nhà thông minh, IoT chủ yếu đóng vai trò gì?",
  "answer": "Kết nối Internet và quản lý thiết bị từ xa",
  "context_token_count": 388,
  "fusion_time": 5.04
}
```

## 🎓 Next Steps

1. **Install dependencies**: `pip install -r requirements_qa.txt`
2. **Check environment**: `python3 check_environment.py`
3. **Run pipeline**: `python3 run_qa_with_fused_contexts.py`
4. **Analyze results**: `python3 analyze_qa_results.py analyze <output>`

## 📚 Documentation Files

- [QA_PIPELINE_README.md](QA_PIPELINE_README.md) - Complete README
- [USAGE.md](USAGE.md) - Detailed usage guide
- [config_qa.py](config_qa.py) - Configuration reference

---

**Version**: 1.0  
**Created**: 2024-05-04  
**LLM Model**: Qwen/Qwen2.5-3B-Instruct  
**Embedding**: AITeamVN/Vietnamese_Embedding_v2 (referenced for context fusion)
