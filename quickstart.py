#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Start: Router-Summary QA Pipeline
Chỉ 3 bước để chạy pipeline:
1. Generate summaries (one-time)
2. Create pipeline
3. Process questions
"""

import json
from pathlib import Path
from pipeline_router_summary import (
    create_summary_generator,
    create_summary_indexer,
    create_qa_pipeline
)
from qa.utils import load_all_chunks, load_doc_chunks


def quickstart_generate_summaries(
    doc_dir: Path = Path("chunk_outputs_finals"),
    output_json: Path = Path("summaries.json"),
    batch_size: int = 10
):
    """
    Generate summaries cho tất cả documents (one-time setup)
    
    Args:
        doc_dir: Directory chứa chunks
        output_json: Output file
        batch_size: Number of documents to process before saving
    """
    print("="*70)
    print("STEP 1: Generate Summaries (Qwen 32B)")
    print("="*70)
    
    generator = create_summary_generator("Qwen/Qwen2.5-32B-Instruct")
    
    # Load documents từ chunks
    print(f"\nLoading documents from {doc_dir}...")
    documents = {}
    
    # Scan doc directories
    for doc_path in sorted(doc_dir.glob("Public*")):
        if doc_path.is_dir():
            doc_id = doc_path.name
            
            # Combine all chunks từ document này
            chunks = load_doc_chunks(doc_dir, doc_id)
            if chunks:
                combined_content = "\n\n".join([c.text for c in chunks])
                documents[doc_id] = combined_content
            
            if len(documents) % batch_size == 0:
                print(f"  Loaded {len(documents)} documents...")
    
    print(f"Total documents: {len(documents)}")
    
    if not documents:
        print("Error: No documents found!")
        return []
    
    # Generate summaries
    print(f"\nGenerating summaries...")
    summaries = generator.generate_summaries_batch(
        documents,
        output_json=output_json
    )
    
    print(f"✓ Summaries saved to {output_json}")
    return summaries


def quickstart_index_summaries(
    summaries_json: Path = Path("summaries.json"),
    chroma_path: Path = Path("chroma_db_summaries")
):
    """
    Index summaries để ready cho query (chạy 1 lần, sau đó reuse)
    
    Args:
        summaries_json: Input summaries file
        chroma_path: ChromaDB path
    """
    print("\n" + "="*70)
    print("STEP 1b: Index Summaries (Setup)")
    print("="*70)
    
    # Load summaries từ JSON
    if not summaries_json.exists():
        print(f"Error: Summaries file not found: {summaries_json}")
        print("Please run: python quickstart.py --generate-summaries")
        return None
    
    with open(summaries_json, 'r', encoding='utf-8') as f:
        summaries = json.load(f)
    
    print(f"Loaded {len(summaries)} summaries")
    
    # Index into ChromaDB
    indexer = create_summary_indexer(
        embedding_model="AITeamVN/Vietnamese_Embedding_v2",
        chroma_db_path=chroma_path,
        json_output_path=summaries_json
    )
    
    indexer.add_summaries(summaries)
    print(f"✓ Summaries indexed to {chroma_path}")
    
    return indexer


def quickstart_create_pipeline(
    chunk_dir: Path = Path("chunk_outputs_finals"),
    summaries_json: Path = Path("summaries.json"),
    chroma_path: Path = Path("chroma_db_summaries")
):
    """
    Create pipeline (ready to answer questions)
    
    Returns:
        Pipeline instance
    """
    print("\n" + "="*70)
    print("STEP 2: Create QA Pipeline")
    print("="*70)
    
    # Load chunks
    print(f"\nLoading chunks from {chunk_dir}...")
    all_chunks = load_all_chunks(chunk_dir)
    print(f"Loaded {len(all_chunks)} chunks")
    
    # Load summary indexer
    indexer = create_summary_indexer(
        embedding_model="AITeamVN/Vietnamese_Embedding_v2",
        chroma_db_path=chroma_path,
        json_output_path=summaries_json
    )
    indexer.load_json()  # Load existing summaries
    
    # Create pipeline
    print(f"\nInitializing QA pipeline...")
    pipeline = create_qa_pipeline(
        all_chunks=all_chunks,
        router_model="Qwen/Qwen1.5B-Chat",
        embedding_model="AITeamVN/Vietnamese_Embedding_v2",
        rerank_model="BAAI/bge-reranker-v2-m3",
        answer_model="Qwen/Qwen2.5-3B-Instruct"
    )
    
    print(f"✓ Pipeline ready!")
    return pipeline


def quickstart_answer_question(pipeline, question: str, options: dict = None):
    """
    Process một question
    
    Args:
        pipeline: QA Pipeline instance
        question: Câu hỏi
        options: Tùy chọn {A: "...", B: "...", ...}
    
    Returns:
        Result dict
    """
    print("\n" + "="*70)
    print("STEP 3: Answer Question")
    print("="*70)
    
    print(f"\nQuestion: {question}")
    if options:
        print("Options:")
        for key, val in options.items():
            print(f"  {key}. {val}")
    
    result = pipeline.process_question(
        question=question,
        options=options
    )
    
    print(f"\nResult:")
    print(f"  Intent: {result['intent']}")
    print(f"  Selected docs: {', '.join(result['selected_docs'])}")
    print(f"  Answer: {result['answer']}")
    if result['reasoning']:
        print(f"  Reasoning: {result['reasoning'][:200]}...")
    
    return result


def main():
    """Main quickstart"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Quick Start - Router-Summary QA Pipeline")
    parser.add_argument("--generate-summaries", action="store_true",
                        help="Generate summaries from documents (one-time setup)")
    parser.add_argument("--interactive", action="store_true",
                        help="Run interactive mode (answer questions)")
    parser.add_argument("--summaries-file", type=Path, default=Path("summaries.json"),
                        help="Summaries JSON file")
    parser.add_argument("--chunk-dir", type=Path, default=Path("chunk_outputs_finals"),
                        help="Chunk directory")
    parser.add_argument("--chroma-path", type=Path, default=Path("chroma_db_summaries"),
                        help="ChromaDB path")
    
    args = parser.parse_args()
    
    # Step 1: Generate summaries (if needed)
    if args.generate_summaries:
        quickstart_generate_summaries(
            doc_dir=args.chunk_dir,
            output_json=args.summaries_file
        )
        print("\n✓ Summaries generated!")
        print("Next: python quickstart.py --interactive")
        return
    
    # Setup summaries index
    print("Setting up summaries index...")
    indexer = quickstart_index_summaries(
        summaries_json=args.summaries_file,
        chroma_path=args.chroma_path
    )
    
    # Create pipeline
    pipeline = quickstart_create_pipeline(
        chunk_dir=args.chunk_dir,
        summaries_json=args.summaries_file,
        chroma_path=args.chroma_path
    )
    
    # Interactive mode
    if args.interactive:
        print("\n" + "="*70)
        print("INTERACTIVE MODE - Ask questions!")
        print("="*70)
        
        while True:
            try:
                print("\n" + "-"*70)
                question = input("Question (or 'quit' to exit): ").strip()
                
                if question.lower() == 'quit':
                    break
                
                if not question:
                    continue
                
                # Ask for options (optional)
                print("Enter options (A: value, leave empty to skip):")
                options = {}
                for letter in ['A', 'B', 'C', 'D']:
                    value = input(f"  {letter}: ").strip()
                    if value:
                        options[letter] = value
                
                # Process question
                result = quickstart_answer_question(
                    pipeline,
                    question,
                    options if options else None
                )
                
            except KeyboardInterrupt:
                break
        
        print("\n✓ Exiting...")
    else:
        # Demo mode
        print("\n" + "="*70)
        print("DEMO MODE - Sample Questions")
        print("="*70)
        
        demo_questions = [
            {
                "question": "Tính 100 + 200 = ?",
                "options": {"A": "300", "B": "250", "C": "350", "D": "400"}
            },
            {
                "question": "Public001 nói về gì?",
                "options": None
            },
            {
                "question": "Giải: 2x + 3 = 7, tìm x",
                "options": {"A": "1", "B": "2", "C": "3", "D": "4"}
            }
        ]
        
        for i, q in enumerate(demo_questions, 1):
            print(f"\n[Question {i}/{len(demo_questions)}]")
            quickstart_answer_question(
                pipeline,
                q["question"],
                q["options"]
            )


if __name__ == "__main__":
    main()
