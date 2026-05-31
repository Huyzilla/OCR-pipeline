# Data Preparation Pipeline

Code is split by training target:

- `data_reranker/`: builds reranker training data.
- `data_embedding/`: builds the master dataset and curriculum JSONL files.

Generated output files are written to this folder, next to this README, not inside
the code folders.

## Reranker Data

From the repository root:

```powershell
python ".\data preparation pipeline\data_reranker\run_pipeline.py" status
python ".\data preparation pipeline\data_reranker\run_pipeline.py" all --dry-run --smoke-n 1
```

Main outputs:

- `retrieve_rerank_991.jsonl`
- `gold_chunks_judged.jsonl`
- `synthesized_negatives.jsonl`
- `synthesized_negatives_answerability_filtered.jsonl`
- `mined_negatives.jsonl`
- `domain_train_final_train.jsonl`
- `domain_train_final_dev.jsonl`

## Embedding Data

From the repository root:

```powershell
python ".\data preparation pipeline\data_embedding\module2_build_master.py"
python ".\data preparation pipeline\data_embedding\module3_split.py"
```

Main outputs:

- `master_dataset.jsonl`
- `train_dataset.jsonl`
- `test_dataset.jsonl`
- `train_stage1.jsonl`
- `train_stage2.jsonl`
- `train_stage3.jsonl`

## Inputs

The code still reads base project inputs from the repository root, including:

- `question.csv`
- `qwen_intent_classification.csv`
- `chunk_outputs_finals/`
- `chroma_db_viettel/`

`data_embedding` prefers source JSONL files in this folder, but falls back to the
legacy `domain_data/` folder when those files have not been copied here yet.
