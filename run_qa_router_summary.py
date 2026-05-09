#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main QA Pipeline Runner: Router-Summary approach
Sử dụng: python run_qa_router_summary.py --question-csv questions.csv
"""

import json
import csv
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime
from pipeline_router_summary import create_qa_pipeline
from qa.utils import load_all_chunks

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def load_questions_csv(csv_file: Path) -> list[dict]:
    """Load questions từ CSV file"""
    print(f"Loading questions from {csv_file}...")
    questions = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            question = row.get('Question', '').strip()
            if not question:
                continue
            
            options = {}
            for letter in ['A', 'B', 'C', 'D']:
                value = row.get(letter, '').strip()
                if value:
                    options[letter] = value
            
            truth = row.get('Truth', '').strip() or None
            
            questions.append({
                'question': question,
                'options': options if options else None,
                'truth': truth
            })
    
    print(f"Loaded {len(questions)} questions")
    return questions


def run_qa_pipeline(
    question_csv: Path,
    chunk_dir: Path,
    output_json: Optional[Path] = None,
    output_csv: Optional[Path] = None,
    max_questions: int = 0,
    router_model: str = "Qwen/Qwen1.5B-Chat",
    embedding_model: str = "AITeamVN/Vietnamese_Embedding_v2",
    rerank_model: str = "BAAI/bge-reranker-v2-m3",
    answer_model: str = "Qwen/Qwen2.5-3B-Instruct",
    context_debug: bool = False
):
    """
    Run full QA pipeline
    
    Args:
        question_csv: Input questions file
        chunk_dir: Chunk directory
        output_json: Output JSON file
        output_csv: Output CSV file
        max_questions: Max questions to process (0 = all)
        router_model: Router model name
        embedding_model: Embedding model name
        rerank_model: Rerank model name
        answer_model: Answer model name
        context_debug: Debug context?
    """
    print("\n" + "="*70)
    print("QA Pipeline - Router-Summary Approach")
    print("="*70)
    
    start_time = datetime.now()
    
    # Load questions
    all_questions = load_questions_csv(question_csv)
    
    if max_questions > 0:
        questions = all_questions[:max_questions]
        print(f"Processing {len(questions)}/{len(all_questions)} questions")
    else:
        questions = all_questions
        print(f"Processing all {len(questions)} questions")
    
    # Load chunks
    print(f"\nLoading chunks from {chunk_dir}...")
    all_chunks = load_all_chunks(chunk_dir)
    print(f"Loaded {len(all_chunks)} chunks")
    
    # Create pipeline
    print(f"\nInitializing QA pipeline...")
    pipeline = create_qa_pipeline(
        all_chunks=all_chunks,
        router_model=router_model,
        embedding_model=embedding_model,
        rerank_model=rerank_model,
        answer_model=answer_model
    )
    
    # Process questions
    print(f"\nProcessing questions...")
    results = pipeline.process_batch(
        questions,
        output_json=output_json,
        output_csv=output_csv,
        context_debug=context_debug and len(questions) > 0
    )
    
    # Print summary
    elapsed = datetime.now() - start_time
    
    print(f"\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Total questions: {len(results)}")
    print(f"Time elapsed: {elapsed}")
    print(f"Time per question: {elapsed.total_seconds() / len(results):.1f}s")
    
    # Accuracy
    has_truth = sum(1 for r in results if r['truth'] is not None)
    if has_truth > 0:
        correct = sum(1 for r in results if r['is_correct'] == True)
        print(f"Accuracy: {correct}/{has_truth} ({correct/has_truth*100:.1f}%)")
        
        # By intent
        by_intent = {}
        for r in results:
            if r['truth'] is None:
                continue
            
            intent = r['intent']
            if intent not in by_intent:
                by_intent[intent] = {'total': 0, 'correct': 0}
            
            by_intent[intent]['total'] += 1
            if r['is_correct']:
                by_intent[intent]['correct'] += 1
        
        print(f"\nAccuracy by intent:")
        for intent, stats in by_intent.items():
            if stats['total'] > 0:
                pct = stats['correct'] / stats['total'] * 100
                print(f"  {intent}: {stats['correct']}/{stats['total']} ({pct:.1f}%)")
    
    print(f"\n✓ Pipeline completed!")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="QA Pipeline - Router-Summary Approach",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all questions
  python run_qa_router_summary.py --question-csv questions.csv
  
  # Process first 100 questions with debug
  python run_qa_router_summary.py --question-csv questions.csv --max-questions 100 --debug
  
  # Custom output paths
  python run_qa_router_summary.py --question-csv questions.csv \\
      --output-json my_results.json --output-csv my_results.csv
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--question-csv",
        type=Path,
        required=True,
        help="Input CSV file with questions (columns: Question, A, B, C, D, Truth)"
    )
    
    # Optional arguments
    parser.add_argument(
        "--chunk-dir",
        type=Path,
        default=Path("chunk_outputs_finals"),
        help="Chunk directory (default: chunk_outputs_finals)"
    )
    
    parser.add_argument(
        "--output-json",
        type=Path,
        default=None,
        help="Output JSON file (default: results_<timestamp>.json)"
    )
    
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=None,
        help="Output CSV file (default: results_<timestamp>.csv)"
    )
    
    parser.add_argument(
        "--max-questions",
        type=int,
        default=0,
        help="Max questions to process (0 = all, default: 0)"
    )
    
    parser.add_argument(
        "--router-model",
        default="gpt-4o-mini",
        help="Router model (default: gpt-4o-mini)"
    )
    
    parser.add_argument(
        "--embedding-model",
        default="AITeamVN/Vietnamese_Embedding_v2",
        help="Embedding model (default: AITeamVN/Vietnamese_Embedding_v2)"
    )
    
    parser.add_argument(
        "--rerank-model",
        default="BAAI/bge-reranker-v2-m3",
        help="Rerank model (default: BAAI/bge-reranker-v2-m3)"
    )
    
    parser.add_argument(
        "--answer-model",
        default="gpt-4o-mini",
        help="Answer model (default: gpt-4o-mini)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.question_csv.exists():
        print(f"Error: Question file not found: {args.question_csv}")
        return 1
    
    if not args.chunk_dir.exists():
        print(f"Error: Chunk directory not found: {args.chunk_dir}")
        return 1
    
    # Set default output paths if not provided
    if args.output_json is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output_json = Path(f"results_{timestamp}.json")
    
    if args.output_csv is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output_csv = Path(f"results_{timestamp}.csv")
    
    # Run pipeline
    try:
        run_qa_pipeline(
            question_csv=args.question_csv,
            chunk_dir=args.chunk_dir,
            output_json=args.output_json,
            output_csv=args.output_csv,
            max_questions=args.max_questions,
            router_model=args.router_model,
            embedding_model=args.embedding_model,
            rerank_model=args.rerank_model,
            answer_model=args.answer_model,
            context_debug=args.debug
        )
        return 0
    
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
