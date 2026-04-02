# OCR Pipeline - Post-Processing Workflow

## 1. Chunking (OCR → Chunks)
- **Script:** `main_chunking.py`
- **Input:** 199 markdown files from `outputs/` (OCR output)
- **Output:** 199 JSON chunk files in `chunk_outputs_final/`
- **Status:** ✅ 199/199 success
- **Config:** 1200 char chunks, 300 overlap, recursive text splitter

## 2. Indexing (Chunks → Vector Indexes)
- **Script:** `indexing.py`
- **Input:** 199 chunk JSON files from `chunk_outputs_final/`
- **Output:** 199 index directories in `indexes/` (dense + sparse)
  - Dense: SentenceTransformer embeddings (384-dim, normalized L2)
  - Sparse: BM25Okapi keyword indexing
- **Status:** ✅ 199/199 success
- **Optimization:** Model loaded once, reused across batch

## 3. LLamaIndex Pipeline (Created but not executed)
- **ingest.py:** Convert chunks → LlamaIndex nodes → ChromaDB storage + SimpleDocumentStore
- **query.py:** Hybrid query engine (vector + BM25 retrieval, reranking, context expansion, Qwen LLM)
- **Status:** ⏸️ Ready but storage not created yet

## 4. Question Answering Tests
- **Dataset:** `question.csv` (100+ questions)
- **Retrieval:** Direct chunk search from `chunk_outputs_final/`
- **Results:**
  - Q1: Answer B (IoT role in smart homes) ✅
  - Q2: Answer B (2010 access control - RFID + facial/fingerprint) ✅

## 5. Technology Stack
- **Embeddings:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384-dim)
- **LLM:** `Qwen/Qwen2.5-3B-Instruct`
- **Reranker:** `BAAI/bge-reranker-base`
- **Vector DB:** ChromaDB
- **Framework:** LlamaIndex + LangChain

## 6. Next Steps (Optional)
- Run `ingest.py` to create LlamaIndex storage context
- Run `query.py` for interactive QA with LLM generation
- Batch evaluate all questions in question.csv
- Measure accuracy across full dataset
