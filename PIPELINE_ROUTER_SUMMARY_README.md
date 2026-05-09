# Router-Summary QA Pipeline

## Overview

Đây là một pipeline QA (Question-Answering) tiên tiến 4 bước với:
1. **Router** (Qwen 1.5B) - Phân loại intent + trích xuất public_id
2. **Summary Index Retrieval** - Tìm top-2 documents từ ~200 doc summaries
3. **Multi-Doc Retrieval** - Hybrid retrieve trong 2 documents → BGE rerank
4. **Answer Generation** (Qwen 3B) - CoT prompt cho tinh_toan, standard cho tra_cuu

### Architecture Diagram

```
Question
   ↓
┌─────────────────────────────────┐
│  Router (Qwen 1.5B)             │
│  - Phân loại: tra_cuu/tinh_toan │
│  - Trích xuất public_id         │
└──────┬──────────────────────────┘
       ↓
┌─────────────────────────────────┐
│ Summary Index Retrieval         │
│ - Embed question                │
│ - Search top-2 documents        │
│ (hoặc dùng public_id nếu có)    │
└──────┬──────────────────────────┘
       ↓
┌──────────────────────────────────┐
│ Multi-Doc Retrieval              │
│ - Hybrid (BM25+Dense) từ 2 docs  │
│ - 5 chunks/doc × 2 = 10 chunks   │
│ - BGE rerank                     │
│ - Top-5 chunks cuối cùng         │
└──────┬──────────────────────────┘
       ↓
┌────────────────────────────────────┐
│ Answer Generation (Qwen 3B)        │
│ - tra_cuu: Standard prompt         │
│ - tinh_toan: CoT prompt            │
└────────────────────────────────────┘
       ↓
     Answer
```

## Installation & Setup

### 1. Prerequisites

```bash
pip install -r requirements.txt
# Thêm:
pip install transformers torch sentence-transformers chromadb rank-bm25
```

### 2. Model Setup

```python
# Models sẽ auto-download từ HuggingFace hub:
# - Qwen/Qwen1.5B-Chat (Router)
# - Qwen/Qwen2.5-32B-Instruct (Summary Generator)
# - Qwen/Qwen2.5-3B-Instruct (Answer Generator)
# - AITeamVN/Vietnamese_Embedding_v2
# - BAAI/bge-reranker-v2-m3
```

## Usage

### Step 1: Generate Summaries (One-time setup)

```python
from pipeline_router_summary import create_summary_generator, create_summary_indexer
from pathlib import Path

# 1.1. Generate summaries từ documents (chỉ cần làm 1 lần)
generator = create_summary_generator("Qwen/Qwen2.5-32B-Instruct")

documents = {
    "Public001": "content...",
    "Public002": "content...",
    # ... 200 documents
}

summaries = generator.generate_summaries_batch(
    documents,
    output_json=Path("summaries.json")
)

# 1.2. Index summaries
indexer = create_summary_indexer()
indexer.add_summaries(summaries)
# → Lưu vào: summaries.json + ChromaDB
```

### Step 2: Setup Chunks

```python
from qa.utils import load_all_chunks
from pathlib import Path

# Load chunks từ chunk_outputs_finals/
all_chunks = load_all_chunks(Path("chunk_outputs_finals"))
```

### Step 3: Create Pipeline & Run

```python
from pipeline_router_summary import create_qa_pipeline

# Create pipeline
pipeline = create_qa_pipeline(
    all_chunks=all_chunks,
    router_model="Qwen/Qwen1.5B-Chat",
    embedding_model="AITeamVN/Vietnamese_Embedding_v2",
    rerank_model="BAAI/bge-reranker-v2-m3",
    answer_model="Qwen/Qwen2.5-3B-Instruct"
)

# Process single question
result = pipeline.process_question(
    question="Tính 100 + 200 = ?",
    options={"A": "300", "B": "250", "C": "350", "D": "400"},
    truth="A"
)

print(f"Intent: {result['intent']}")
print(f"Answer: {result['answer']}")
print(f"Correct: {result['is_correct']}")
```

### Step 4: Batch Processing

```python
questions = [
    {
        "question": "Question 1",
        "options": {"A": "...", "B": "...", ...},
        "truth": "A"
    },
    {
        "question": "Question 2",
        "options": None,
        "truth": None
    }
]

results = pipeline.process_batch(
    questions,
    output_json=Path("results.json"),
    output_csv=Path("results.csv")
)
```

## Components Detail

### 1. Router (router.py)

```python
from pipeline_router_summary import create_router

router = create_router("Qwen/Qwen1.5B-Chat")

result = router.route("Tính 100 + 200 = ?")
# {
#   "question": "Tính 100 + 200 = ?",
#   "intent": "tinh_toan",
#   "public_ids": [],
#   "has_public_id": False
# }
```

**Features:**
- Intent classification: `tra_cuu` (lookup) vs `tinh_toan` (calculation)
- Public ID extraction: Detects references like `Public001`, `Public002`

### 2. Summary Generator (summary_generator.py)

```python
from pipeline_router_summary import create_summary_generator

generator = create_summary_generator("Qwen/Qwen2.5-32B-Instruct")

summary = generator.generate_summary("Public001", document_content)
# {
#   "doc_id": "Public001",
#   "summary_text": "...",
#   "chunk_count": 5,
#   "token_count": 165
# }
```

**Summary Format (~150-200 tokens):**
```
[Topic sentence]
[Key concepts and terms]
[Content type: theory/practice/regulation]
```

### 3. Summary Indexer (summary_indexer.py)

```python
from pipeline_router_summary import create_summary_indexer

indexer = create_summary_indexer()
indexer.add_summaries(summaries)

# Search summaries
results = indexer.search_summaries("Chính sách lương", top_k=2)
# [{doc_id, summary_text, distance, chunk_count, token_count}]
```

**Storage:**
- **JSON**: `summaries.json` - Backup, dễ debug
- **ChromaDB**: `chroma_db_summaries/` - Runtime search

### 4. Multi-Doc Retrieval (multi_doc_retrieval.py)

```python
from pipeline_router_summary.multi_doc_retrieval import MultiDocPipeline

retriever = MultiDocPipeline(
    summary_indexer=indexer,
    all_chunks=all_chunks,
    embedding_model="AITeamVN/Vietnamese_Embedding_v2",
    rerank_model="BAAI/bge-reranker-v2-m3"
)

retrieved, doc_ids = retriever.retrieve_for_question(
    question="Câu hỏi",
    public_ids=None,
    use_summary_search=True
)
```

**Retrieval Process:**
1. Summary search → Top-2 documents
2. Hybrid retrieval (BM25 + Dense) từ mỗi doc → 5 chunks/doc
3. Merge 10 chunks
4. BGE rerank
5. Top-5 chunks cuối cùng (~2000 tokens)

### 5. Answer Generator (answer_generator.py)

```python
from pipeline_router_summary import create_answer_generator

generator = create_answer_generator("Qwen/Qwen2.5-3B-Instruct")

# tra_cuu intent
answer = generator.generate_answer(
    context=context,
    question="Tìm thông tin gì?",
    intent="tra_cuu",
    options={"A": "...", "B": "...", ...}
)

# tinh_toan intent (CoT)
answer = generator.generate_answer(
    context=context,
    question="Tính bao nhiêu?",
    intent="tinh_toan",
    options={"A": "...", "B": "...", ...}
)
```

**Prompts:**

**tra_cuu (Standard):**
```
Dựa vào thông tin sau, trả lời câu hỏi một cách ngắn gọn và chính xác.

CONTEXT:
{context}

QUESTION:
{question}

OPTIONS:
A. {A}
B. {B}
C. {C}
D. {D}

ANSWER:
```

**tinh_toan (CoT):**
```
Dựa vào thông tin sau, giải từng bước rồi trả lời.

CONTEXT:
{context}

QUESTION:
{question}

Hướng dẫn giải:
Bước 1 - Xác định số liệu: Liệt kê các con số/dữ kiện liên quan
Bước 2 - Tính toán: Thực hiện từng phép tính, ghi rõ công thức
Bước 3 - Đối chiếu: So kết quả với từng đáp án A, B, C, D
Bước 4 - Kết luận: Chọn đáp án đúng

ANSWER:
```

## Demo Script

```bash
# Run all steps
python demo_pipeline.py

# Run specific step
python demo_pipeline.py --step 1  # Router demo
python demo_pipeline.py --step 2  # Summary generation
python demo_pipeline.py --step 3  # Summary indexing
python demo_pipeline.py --step 4  # Full pipeline

# Custom output directory
python demo_pipeline.py --output-dir ./my_demo_output
```

## File Structure

```
pipeline_router_summary/
├── __init__.py                 # Package initialization
├── router.py                   # Intent + Public ID detection
├── summary_generator.py        # Generate summaries (Qwen 32B)
├── summary_indexer.py          # Store in JSON + ChromaDB
├── multi_doc_retrieval.py      # Hybrid retrieve + rerank
├── answer_generator.py         # Generate answers (Qwen 3B)
└── pipeline.py                 # Main orchestration

demo_pipeline.py               # Complete demo script

PIPELINE_ROUTER_SUMMARY_README.md  # This file
```

## Key Design Decisions

### 1. Why Summary Indexing?

**Problem:** Search trong 200 documents is expensive
**Solution:** Create summaries (~150-200 tokens) → Search summaries first → Top-2 documents

**Benefits:**
- Fast initial filtering
- Efficient summary-level relevance scoring
- Fallback to full retrieval only for top documents

### 2. Why Multi-Doc Retrieval?

**Pattern:** Questions often reference 1-2 documents
**Approach:**
- If public_id in question → use it
- Else → use summary search

**5 chunks/doc:**
- Enough to cover document information
- Not too many (reranker still effective)
- ~2000 tokens total after reranking

### 3. Why CoT for tinh_toan?

**Observation:** Math/calculation questions need step-by-step reasoning
**Solution:** Use Chain-of-Thought prompt for tinh_toan intent

**tra_cuu:** Direct answer sufficient
**tinh_toan:** Show reasoning → Higher accuracy

### 4. Dual Storage for Summaries

**JSON:** Backup + easy inspection
**ChromaDB:** Runtime efficiency + vector search

**Why both?**
- If ChromaDB resets → no need to re-generate
- Easy to audit/debug summaries
- Can rebuild ChromaDB from JSON

## Performance Considerations

### Memory Usage
- Router: ~2-3 GB (1.5B model)
- Summary Generator: ~20-30 GB (32B model) → One-time only
- Answer Generator: ~3-4 GB (3B model)
- Embedding Model: ~1-2 GB

### Speed
- Router: ~0.5s/question
- Summary Search: ~0.1s
- Multi-Doc Retrieve: ~2-5s
- Answer Generation: ~5-10s
- **Total: ~10-20s/question**

### Optimization Tips
1. Batch process questions
2. Cache embeddings (already done)
3. Use GPU for all components
4. Consider 4-bit quantization for large models if memory constrained

## Troubleshooting

### CUDA Out of Memory
```python
# Use smaller models or enable 4-bit quantization
# In summary_generator.py:
# load_in_4bit=True
```

### Low Accuracy
1. Check summary quality → regenerate if needed
2. Verify chunking is correct
3. Ensure correct embedding model is used
4. Test router intent detection

### Slow Retrieval
1. Check ChromaDB is being used (not generating on-the-fly)
2. Verify GPU usage
3. Consider batch processing

## Next Steps / Future Improvements

1. **Adaptive Summary Length:** Adjust based on document type
2. **Query Expansion:** Generate alternative queries for better retrieval
3. **Few-shot Learning:** Add examples to prompts for better accuracy
4. **Hybrid Ranking:** Combine BM25/Dense/CoT reasoning for final ranking
5. **Cache Management:** Cache frequently asked questions
6. **A/B Testing:** Compare different router models
7. **Fine-tuning:** Fine-tune router on domain-specific data

## References

- Qwen Models: https://huggingface.co/Qwen
- BGE Reranker: https://huggingface.co/BAAI/bge-reranker-v2-m3
- ChromaDB: https://docs.trychroma.com
- Chain-of-Thought Prompting: https://arxiv.org/abs/2201.11903
