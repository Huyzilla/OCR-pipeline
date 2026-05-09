#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run pipeline router for a single question and update output files.

Pipeline flow:
1. Router: Phân loại intent (tra_cuu/tinh_toan) + extract public_id từ regex Public_XXX
2. If public_id found in question:
   - Use direct document IDs
   Else:
   - Search summary index → top-2 documents
3. Multi-doc retrieval:
   - Hybrid BM25 + Dense retrieval (5 chunks/doc)
   - Merge 10 chunks + BGE rerank
   - Top-5 chunks final
4. Answer generation:
   - tra_cuu: Standard prompt
   - tinh_toan: CoT prompt (max_tokens=512)
   - Model: gpt-4o-mini (loaded from OPENAI_API_KEY env)
5. Save to JSON + CSV
"""

import json
import csv
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline_router_summary import create_qa_pipeline
from qa.utils import load_all_chunks, parse_answer_text

def main():
    """Run pipeline for single question"""
    print("=" * 70)
    print("Pipeline Router: Single Question Executor")
    print("=" * 70)
    
    # Check API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠ WARNING: OPENAI_API_KEY not set in environment!")
        return
    
    # Load chunks
    print("\n[STEP 1] Loading chunks from chunk_outputs_finals/...")
    all_chunks = load_all_chunks(Path("chunk_outputs_finals"))
    print(f"  ✓ Loaded {len(all_chunks)} total chunks")
    
    # Create pipeline
    print("\n[STEP 2] Creating pipeline components...")
    print("  - Router (Qwen2.5 1.5B Instruct): Intent classification + Public ID extraction")
    print("  - Summary Indexer: ChromaDB search for top-2 documents")
    print("  - Multi-Doc Retriever: Hybrid BM25+Dense + BGE rerank")
    print("  - Answer Generator: gpt-4o-mini (OpenAI API)")
    pipeline = create_qa_pipeline(
        all_chunks=all_chunks,
        router_model="Qwen/Qwen2.5-1.5B-Instruct",
        embedding_model="AITeamVN/Vietnamese_Embedding_v2",
        rerank_model="BAAI/bge-reranker-v2-m3",
        answer_model="gpt-4o-mini"  # Using OpenAI API
    )
    print("  ✓ Pipeline initialized")

    # Load output_pipeline.json
    print("\n[STEP 3] Loading question from output_pipeline.json...")
    output_json_path = Path("output_pipeline.json")
    with open(output_json_path, 'r', encoding='utf-8') as f:
        all_results = json.load(f)
    
    # Get question index from argument or use last one
    # User can modify q_index to run different question
    q_index = 177  # ← CHANGE THIS TO RUN DIFFERENT QUESTION (0-indexed)
    
    q_data = all_results[q_index]
    
    print(f"\n  Question Index: {q_data['question_Index']}")
    print(f"  Question: {q_data['question'][:100]}...")
    print(f"  Previous answer: {q_data['answer'][:60] if q_data['answer'] else '(empty)'}...")
    
    # Run pipeline for this question
    print(f"\n[STEP 4] Running pipeline for question {q_data['question_Index']}...")
    print("  ├─ Router: Detecting intent + extracting public_ids from regex...")
    result = pipeline.process_question(
        question=q_data["question"],
        options=q_data.get("options"),
        truth=q_data.get("truth"),
        context_debug=False  # Set to True to see chunk details
    )
    
    print(f"  │")
    print(f"  ├─ Router Results:")
    print(f"  │  ├─ Intent: {result['intent']}")
    print(f"  │  └─ Public IDs extracted: {result['public_ids'] if result['public_ids'] else '(none)'}")
    print(f"  │")
    print(f"  ├─ Retrieval Results:")
    print(f"  │  ├─ Selected documents: {result['selected_docs']}")
    print(f"  │  ├─ Context length: {len(result['context'])} chars")
    print(f"  │")
    print(f"  └─ Answer Generation:")
    print(f"     ├─ Answer: {result['answer'][:80]}...")
    if result['reasoning']:
        print(f"     ├─ Reasoning (first 100 chars): {result['reasoning'][:100]}...")
    print(f"     └─ Model: gpt-4o-mini (max_tokens=512)")
    
    # Update the result in all_results
    print(f"\n[STEP 5] Updating output files...")
    all_results[q_index] = {
        "question_Index": q_data["question_Index"],
        "question": result["question"],
        "intent": result["intent"],
        "public_ids": result["public_ids"],
        "selected_docs": result["selected_docs"],
        "context": result["context"],
        "answer": result["answer"],
        "reasoning": result["reasoning"],
        "truth": result["truth"],
        "is_correct": result["is_correct"]
    }
    
    # Save to JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Saved to {output_json_path}")
    
    # Update CSV
    print(f"  ✓ Updating {Path('output_pipeline.csv').name}...")
    output_csv_path = Path("output_pipeline.csv")
    
    # Read all CSV rows
    csv_rows = []
    with open(output_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        csv_rows = list(reader)
    
    # Update row for this question
    ans_str = result["answer"]
    answers = parse_answer_text(ans_str)
    
    if not answers:
        num_correct = 0
        ans_col = ""
    else:
        num_correct = len(answers)
        ans_col = ",".join(answers)
    
    csv_rows[q_index] = [str(num_correct), ans_col]
    
    # Write back to CSV
    with open(output_csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_rows)
    print(f"  ✓ Saved to {output_csv_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("RESULT SUMMARY")
    print("=" * 70)
    print(f"Question Index: {result['question']}")
    print(f"\nIntent Classification: {result['intent']}")
    print(f"  ├─ Indicates: {'tra_cuu (lookup)' if result['intent']=='tra_cuu' else 'tinh_toan (calculation)'}")
    
    print(f"\nDocument Retrieval:")
    print(f"  ├─ Public IDs extracted: {result['public_ids'] if result['public_ids'] else '(none, used summary search)'}")
    print(f"  ├─ Selected documents: {result['selected_docs']}")
    print(f"  ├─ Context (merged chunks): {len(result['context'])} chars")
    
    print(f"\nAnswer:")
    print(f"  ├─ Extracted answers: {','.join(parse_answer_text(result['answer'])) if parse_answer_text(result['answer']) else '(empty)'}")
    print(f"  ├─ Full answer: {result['answer'][:100]}...")
    if result['reasoning']:
        print(f"  ├─ Reasoning: {result['reasoning'][:150]}...")
    
    print(f"\nOutput Files Updated:")
    print(f"  ├─ output_pipeline.json: Row {q_data['question_Index']}")
    print(f"  ├─ output_pipeline.csv: [{num_correct}, '{ans_col}']")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
