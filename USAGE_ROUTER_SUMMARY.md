# Router-Summary QA Pipeline - Usage Guide

## Quick Reference

### One-time Setup (Generate Summaries)
```bash
# Generate summaries từ tất cả 200 documents
python quickstart.py --generate-summaries

# Output: summaries.json
```

### Run Pipeline (Interactive)
```bash
# Chat with the pipeline
python quickstart.py --interactive

# Input: Questions
# Output: Answers with intent, reasoning, selected documents
```

### Run Pipeline (Batch)
```bash
# Process CSV file với questions
python run_qa_router_summary.py \
    --question-csv questions.csv \
    --output-json results.json \
    --output-csv results.csv
```

---

## Detailed Usage Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements_pipeline.txt
```

### Step 2: Prepare Documents

Your documents should already be chunked in `chunk_outputs_finals/`:
```
chunk_outputs_finals/
├── Public001/
│   ├── Public001-chunk-0.json
│   ├── Public001-chunk-1.json
│   └── ...
├── Public002/
├── Public003/
└── ...
```

### Step 3: Generate Summaries (One-time)

**Why:** Create 150-200 token summaries for each document to enable fast retrieval

**How:**
```bash
python quickstart.py --generate-summaries

# Or more control:
python summary_manager.py generate \
    --chunk-dir chunk_outputs_finals \
    --output summaries.json

# Or specific documents:
python summary_manager.py generate \
    --chunk-dir chunk_outputs_finals \
    --output summaries.json \
    --docs Public001 Public002 Public003
```

**Output:**
- `summaries.json` - Backup, easy inspection
  ```json
  [
    {
      "doc_id": "Public001",
      "summary_text": "...(150-200 tokens)...",
      "chunk_count": 5,
      "token_count": 165
    },
    ...
  ]
  ```
- `chroma_db_summaries/` - Vector database for fast search

**Time:** ~10-30 seconds per document (depends on GPU)

### Step 4: Create Questions File

Format: CSV with columns `Question`, `A`, `B`, `C`, `D`, `Truth` (optional)

**Example: questions.csv**
```csv
Question,A,B,C,D,Truth
Tính 100 + 200 = ?,250,300,350,400,B
Public001 nói gì?,Lương cố định,Lương linh hoạt,Không biết,Không có,A
```

### Step 5: Run Pipeline

**Option A: Quick Start (Interactive)**
```bash
python quickstart.py --interactive

# Prompts:
# Question (or 'quit' to exit): [your question]
# Enter options (A: value, leave empty to skip):
#   A: [option A]
#   B: [option B]
#   C: [option C]
#   D: [option D]
```

**Option B: Batch Processing**
```bash
python run_qa_router_summary.py \
    --question-csv questions.csv \
    --chunk-dir chunk_outputs_finals \
    --output-json results.json \
    --output-csv results.csv \
    --max-questions 100
```

**Output files:**

1. `results.json`:
```json
[
  {
    "question": "Tính 100 + 200 = ?",
    "intent": "tinh_toan",
    "public_ids": [],
    "selected_docs": ["Public015", "Public042"],
    "context": "...(top-5 chunks)...",
    "answer": "B",
    "reasoning": "Bước 1: 100 + 200 = 300...",
    "truth": "B",
    "is_correct": true
  },
  ...
]
```

2. `results.csv`:
```
question,intent,public_ids,selected_docs,answer,truth,is_correct
"Tính 100 + 200 = ?",tinh_toan,"","Public015,Public042","B","B",true
```

### Step 6: Analyze Results

**Check accuracy:**
```bash
python -c "
import json
with open('results.json') as f:
    results = json.load(f)
    correct = sum(1 for r in results if r['is_correct'] == True)
    total = len(results)
    print(f'Accuracy: {correct}/{total} = {correct/total*100:.1f}%')
"
```

**Check by intent:**
```bash
python -c "
import json
from collections import Counter
with open('results.json') as f:
    results = json.load(f)
    by_intent = {}
    for r in results:
        intent = r['intent']
        if intent not in by_intent:
            by_intent[intent] = {'total': 0, 'correct': 0}
        by_intent[intent]['total'] += 1
        if r['is_correct']:
            by_intent[intent]['correct'] += 1
    
    for intent, stats in by_intent.items():
        pct = stats['correct']/stats['total']*100
        print(f'{intent}: {stats[\"correct\"]}/{stats[\"total\"]} ({pct:.1f}%)')
"
```

---

## Advanced Usage

### Manage Summaries

**Inspect summaries:**
```bash
python summary_manager.py inspect --summaries summaries.json --samples 5
```

**Search summaries:**
```bash
python summary_manager.py search "Chính sách lương" --top-k 3
```

**Export to CSV:**
```bash
python summary_manager.py export \
    --summaries summaries.json \
    --output summaries.csv
```

**Rebuild ChromaDB index:**
```bash
python summary_manager.py rebuild \
    --summaries summaries.json \
    --chroma chroma_db_summaries
```

**Show statistics:**
```bash
python summary_manager.py stats --summaries summaries.json
```

### Custom Pipeline

```python
from pathlib import Path
from pipeline_router_summary import create_qa_pipeline
from qa.utils import load_all_chunks

# Load data
all_chunks = load_all_chunks(Path("chunk_outputs_finals"))

# Create pipeline with custom models
pipeline = create_qa_pipeline(
    all_chunks=all_chunks,
    router_model="Qwen/Qwen1.5B-Chat",
    embedding_model="AITeamVN/Vietnamese_Embedding_v2",
    rerank_model="BAAI/bge-reranker-v2-m3",
    answer_model="Qwen/Qwen2.5-3B-Instruct"
)

# Process question
result = pipeline.process_question(
    question="Your question?",
    options={"A": "...", "B": "...", "C": "...", "D": "..."},
    truth="A"  # Optional
)

print(result)
```

### Component-level Usage

**Just Router:**
```python
from pipeline_router_summary import create_router

router = create_router()
result = router.route("Tính 100 + 200")
print(result)
# {intent: "tinh_toan", public_ids: [], ...}
```

**Just Retrieval:**
```python
from pipeline_router_summary import create_summary_indexer
from pipeline_router_summary.multi_doc_retrieval import MultiDocPipeline
from qa.utils import load_all_chunks

indexer = create_summary_indexer()
indexer.load_json()  # Load existing summaries

all_chunks = load_all_chunks(Path("chunk_outputs_finals"))
retriever = MultiDocPipeline(indexer, all_chunks)

chunks, docs = retriever.retrieve_for_question(
    "Your question",
    use_summary_search=True
)
```

**Just Answer Generation:**
```python
from pipeline_router_summary import create_answer_generator

generator = create_answer_generator()

answer = generator.generate_answer(
    context="Context from retrieved chunks",
    question="Your question",
    intent="tinh_toan",  # or "tra_cuu"
    options={"A": "...", "B": "..."}
)
```

---

## Configuration

### Model Configuration

Edit model names in:

1. **quickstart.py**:
```python
# Line ~180-190
pipeline = create_qa_pipeline(
    router_model="Qwen/Qwen1.5B-Chat",
    answer_model="Qwen/Qwen2.5-3B-Instruct"
)
```

2. **pipeline.py**:
```python
# Line ~80-90
def __init__(self, ...,
    router_model: str = "Qwen/Qwen1.5B-Chat",
    answer_model: str = "Qwen/Qwen2.5-3B-Instruct"
):
```

### Environment Variables

```bash
# Use specific GPU
export CUDA_VISIBLE_DEVICES=0

# Increase memory limit
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# HF token (if needed)
export HF_TOKEN=your_token
```

### Performance Tuning

**For limited memory:**
```python
# Use 4-bit quantization in summary_generator.py
load_in_4bit=True

# Or use smaller models
router_model="Qwen/Qwen0.5B-Chat"  # Smaller router
answer_model="Qwen/Qwen1.5B-Instruct"  # Smaller answer model
```

**For speed:**
```python
# Batch processing is faster than one-by-one
results = pipeline.process_batch(questions)  # ~10s/question vs ~15s individual
```

---

## Troubleshooting

### CUDA Out of Memory
```bash
# Reduce batch size or use 4-bit quantization
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Or use CPU (slow!)
export CUDA_VISIBLE_DEVICES=-1
```

### Models not downloading
```bash
# Set HuggingFace cache directory
export HF_HOME=/path/to/cache

# Or login to HuggingFace
huggingface-cli login
```

### ChromaDB errors
```bash
# Reset chromadb
rm -rf chroma_db_summaries/

# Rebuild from json
python summary_manager.py rebuild
```

### Low accuracy
1. Check summary quality:
```bash
python summary_manager.py inspect
```

2. Verify chunks:
```bash
python -c "
from qa.utils import load_all_chunks
from pathlib import Path
chunks = load_all_chunks(Path('chunk_outputs_finals'))
print(f'Total chunks: {len(chunks)}')
for i, c in enumerate(chunks[:3]):
    print(f'{i}. {c.chunk_id}: {len(c.text)} chars')
"
```

3. Test router intent detection:
```bash
python -c "
from pipeline_router_summary import create_router
router = create_router()
for q in ['Tính 100+200', 'Tìm thông tin', 'Giải bài toán']:
    print(router.route(q)['intent'])
"
```

---

## Performance Metrics

### Speed (on V100 GPU)
| Operation | Time |
|-----------|------|
| Router (per question) | 0.5s |
| Summary search | 0.1s |
| Multi-doc retrieve | 2-5s |
| Answer generation | 5-10s |
| **Total (per question)** | **~10-20s** |

### Memory Usage
| Component | Memory |
|-----------|--------|
| Router (1.5B) | 2-3 GB |
| Summary Generator (32B) | 20-30 GB* |
| Answer Generator (3B) | 3-4 GB |
| Embedding Model | 1-2 GB |
| **Total** | **~30-40 GB** |
*Generator only needed for summary generation, not during inference

---

## Next Steps

1. Generate summaries for all 200 documents
2. Test with sample questions
3. Analyze accuracy by intent
4. Fine-tune models if needed
5. Deploy to production

See [PIPELINE_ROUTER_SUMMARY_README.md](PIPELINE_ROUTER_SUMMARY_README.md) for more details.
