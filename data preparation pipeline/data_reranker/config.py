from __future__ import annotations

from pathlib import Path


PIPELINE_DIR = Path(__file__).resolve().parent
PIPELINE_ROOT = PIPELINE_DIR.parent
REPO_ROOT = PIPELINE_ROOT.parent
OUTPUT_ROOT = PIPELINE_ROOT
DOMAIN_DATA = OUTPUT_ROOT
DATA_DIR = REPO_ROOT / "data"

# Inputs
QUESTION_CSV = DATA_DIR / "question.csv"
INTENT_CSV = DATA_DIR / "qwen_intent_classification.csv"
CHUNK_DIR = REPO_ROOT / "chunk_outputs_finals"
CHROMA_PATH = REPO_ROOT / "chroma_db_viettel"

# Intermediate outputs
RETRIEVE_OUTPUT = OUTPUT_ROOT / "retrieve_rerank_991.jsonl"
JUDGED_OUTPUT = DOMAIN_DATA / "gold_chunks_judged.jsonl"
SYNTHESIZED_OUTPUT = DOMAIN_DATA / "synthesized_negatives.jsonl"
SYNTHESIZED_FILTERED_OUTPUT = DOMAIN_DATA / "synthesized_negatives_answerability_filtered.jsonl"
SYNTHESIZED_REMOVED_OUTPUT = DOMAIN_DATA / "synthesized_negatives_removed_answerable.jsonl"
ANSWERABILITY_CACHE = DOMAIN_DATA / "answerability_judge_cache.jsonl"
MINED_OUTPUT = DOMAIN_DATA / "mined_negatives.jsonl"

# Final outputs
TRAIN_OUTPUT = DOMAIN_DATA / "domain_train_final_train.jsonl"
DEV_OUTPUT = DOMAIN_DATA / "domain_train_final_dev.jsonl"

# Models / knobs
EMBEDDING_MODEL = "AITeamVN/Vietnamese_Embedding_v2"
RERANK_MODEL = "BAAI/bge-reranker-v2-m3"
ANSWERABILITY_MODEL = "gpt-4o-mini"
TOP_K = 20
MAX_EASY = 0
DEV_RATIO = 0.1
SEED = 42
