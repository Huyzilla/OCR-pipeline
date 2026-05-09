#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Pipeline Orchestration: Router → Summary Search → Multi-Doc Retrieve → Answer
"""

import json
import csv
from pathlib import Path
from typing import Optional, TypedDict
from tqdm import tqdm

from .router import QuestionRouter, RouterResult
from .summary_indexer import SummaryIndexer
from .multi_doc_retrieval import MultiDocPipeline, RetrievedChunk
from .answer_generator import AnswerGenerator, AnswerResult

try:
    from qa.utils import ChunkRecord, parse_answer_text
except ImportError:
    # Fallback for when running as submodule
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from qa.utils import ChunkRecord, parse_answer_text


class QAPipelineInput(TypedDict):
    """Input cho QA pipeline"""
    question: str
    options: Optional[dict]
    truth: Optional[str]


class QAPipelineOutput(TypedDict):
    """Output từ QA pipeline"""
    question: str
    intent: str
    public_ids: list[str]
    selected_docs: list[str]
    context: str
    answer: str
    reasoning: str
    truth: Optional[str]
    is_correct: Optional[bool]


class RouterSummaryQAPipeline:
    """
    Full pipeline:
    1. Router (Qwen 1.5B) - Intent + Public ID
    2. Summary Search - Top-2 documents
    3. Multi-Doc Retrieval - Hybrid + Rerank
    4. Answer Generation (Qwen 3B) - CoT/Standard
    """
    
    def __init__(
        self,
        all_chunks: list[ChunkRecord],
        router_model: str = "Qwen/Qwen2.5-1.5B-Instruct",
        summary_indexer: Optional[SummaryIndexer] = None,
        embedding_model: str = "AITeamVN/Vietnamese_Embedding_v2",
        rerank_model: str = "BAAI/bge-reranker-v2-m3",
        answer_model: str = "Qwen/Qwen2.5-3B-Instruct"
    ):
        """
        Initialize pipeline
        
        Args:
            all_chunks: List of all ChunkRecord
            router_model: Router model name
            summary_indexer: SummaryIndexer instance
            embedding_model: Embedding model name
            rerank_model: Rerank model name
            answer_model: Answer generation model name
        """
        print("=" * 60)
        print("Initializing RouterSummaryQAPipeline")
        print("=" * 60)
        
        # Initialize components
        print("\n[1/4] Initializing Router...")
        self.router = QuestionRouter(router_model)
        
        print("\n[2/4] Initializing Summary Indexer...")
        if summary_indexer is None:
            # Resolve path tương đối so với thư mục gốc của project (không phụ thuộc vào cwd)
            _project_root = Path(__file__).parent.parent
            self.summary_indexer = SummaryIndexer(
                embedding_model=embedding_model,
                chroma_db_path=_project_root / "chroma_db_summaries",
                json_output_path=_project_root / "summaries.json"
            )
        else:
            self.summary_indexer = summary_indexer
        
        print("\n[3/4] Initializing Multi-Doc Pipeline...")
        self.multi_doc_pipeline = MultiDocPipeline(
            summary_indexer=self.summary_indexer,
            all_chunks=all_chunks,
            embedding_model=embedding_model,
            rerank_model=rerank_model
        )
        
        print("\n[4/4] Initializing Answer Generator...")
        self.answer_generator = AnswerGenerator(answer_model)
        
        print("\n" + "=" * 60)
        print("Pipeline initialized successfully!")
        print("=" * 60)
    
    def process_question(
        self,
        question: str,
        options: Optional[dict] = None,
        truth: Optional[str] = None,
        context_debug: bool = False
    ) -> QAPipelineOutput:
        """
        Process một question từ đầu tới cuối
        
        Args:
            question: Câu hỏi
            options: {A: "...", B: "...", ...}
            truth: Correct answer (nếu có)
            context_debug: Print debug info?
            
        Returns:
            QAPipelineOutput
        """
        output: QAPipelineOutput = {
            "question": question,
            "intent": "",
            "public_ids": [],
            "selected_docs": [],
            "context": "",
            "answer": "",
            "reasoning": "",
            "truth": truth,
            "is_correct": None
        }
        
        # Step 1: Router
        print(f"\n[Router] Processing: {question[:60]}...")
        router_result: RouterResult = self.router.route(question)
        output["intent"] = router_result["intent"]
        output["public_ids"] = router_result["public_ids"]
        print(f"  Intent: {router_result['intent']}, Public IDs: {router_result['public_ids']}")
        
        # Step 2: Summary Search → Multi-Doc Retrieve
        print(f"\n[Retrieval] Searching summaries and retrieving chunks...")
        retrieved_chunks, selected_docs = self.multi_doc_pipeline.retrieve_for_question(
            question,
            public_ids=router_result["public_ids"],
            use_summary_search=True
        )
        output["selected_docs"] = selected_docs
        
        if not retrieved_chunks:
            print("  ⚠ No chunks retrieved!")
            return output
        
        print(f"  Retrieved {len(retrieved_chunks)} chunks from {len(set([c['doc_id'] for c in retrieved_chunks]))} documents")
        
        # Build context
        context_parts = []
        for chunk in retrieved_chunks:
            context_parts.append(chunk["text"])
        context = "\n\n".join(context_parts)
        output["context"] = context
        
        if context_debug:
            print(f"\n[Debug] Context length: {len(context)} chars")
            print(f"[Debug] Retrieved chunks:")
            for i, c in enumerate(retrieved_chunks[:3]):  # Show first 3
                print(f"  {i+1}. {c['chunk_id']}: {c['text'][:80]}...")
        
        # Step 3: Answer Generation
        print(f"\n[Answer] Generating answer (intent: {router_result['intent']})...")
        answer_result: AnswerResult = self.answer_generator.generate_answer(
            context=context,
            question=question,
            intent=router_result["intent"],
            options=options
        )
        output["answer"] = answer_result["answer"]
        output["reasoning"] = answer_result["reasoning"]
        print(f"  Answer: {answer_result['answer']}")
        
        # Check correctness
        if truth:
            is_correct = answer_result["answer"].strip().upper() == truth.strip().upper()
            output["is_correct"] = is_correct
            print(f"  Correct: {is_correct} (truth: {truth})")
        
        return output
    
    def process_batch(
        self,
        questions: list[QAPipelineInput],
        output_json: Optional[Path] = None,
        output_csv: Optional[Path] = None,
        context_debug: bool = False
    ) -> list[QAPipelineOutput]:
        """
        Process batch questions
        
        Args:
            questions: List of QAPipelineInput
            output_json: Output JSON file path
            output_csv: Output CSV file path
            context_debug: Debug mode?
            
        Returns:
            List of QAPipelineOutput
        """
        print(f"\n{'='*60}")
        print(f"Processing {len(questions)} questions")
        print(f"{'='*60}")
        
        results = []
        
        for i, q_input in enumerate(tqdm(questions, desc="Processing questions"), 1):
            result = self.process_question(
                question=q_input["question"],
                options=q_input.get("options"),
                truth=q_input.get("truth"),
                context_debug=context_debug and i == 1  # Debug first question only
            )
            results.append(result)
            
            # Incremental save
            if output_json:
                output_json.parent.mkdir(parents=True, exist_ok=True)
                with open(output_json, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            
            if output_csv:
                output_csv.parent.mkdir(parents=True, exist_ok=True)
                with open(output_csv, 'w', encoding='utf-8', newline='') as f:
                    # Không ghi header, ghi trực tiếp kết quả để tiện chấm điểm
                    # Format: num_correct,"A,B"
                    writer = csv.writer(f)
                    
                    for r in results:
                        ans_str = r["answer"]
                        answers = parse_answer_text(ans_str)
                        
                        if not answers:
                            num_correct = 0
                            ans_col = ""
                        else:
                            num_correct = len(answers)
                            ans_col = ",".join(answers)
                            
                        writer.writerow([num_correct, ans_col])
                        
        if output_json:
            print(f"\n✓ Results saved to {output_json}")
        if output_csv:
            print(f"✓ CSV results saved to {output_csv}")
        
        # Print statistics
        total = len(results)
        correct = sum(1 for r in results if r["is_correct"] == True)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        intent_counts = {}
        for r in results:
            intent = r["intent"]
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        print(f"\n{'='*60}")
        print("Results Summary:")
        print(f"{'='*60}")
        print(f"Total questions: {total}")
        print(f"Correct answers: {correct}/{total} ({accuracy:.1f}%)")
        print(f"\nIntent distribution:")
        for intent, count in intent_counts.items():
            print(f"  - {intent}: {count}")
        
        return results


def create_qa_pipeline(
    all_chunks: list[ChunkRecord],
    router_model: str = "Qwen/Qwen2.5-1.5B-Instruct",
    embedding_model: str = "AITeamVN/Vietnamese_Embedding_v2",
    rerank_model: str = "BAAI/bge-reranker-v2-m3",
    answer_model: str = "Qwen/Qwen2.5-3B-Instruct"
) -> RouterSummaryQAPipeline:
    """Factory function"""
    return RouterSummaryQAPipeline(
        all_chunks=all_chunks,
        router_model=router_model,
        embedding_model=embedding_model,
        rerank_model=rerank_model,
        answer_model=answer_model
    )


if __name__ == "__main__":
    print("Router-Summary QA Pipeline Module")
    print("Use this as part of the complete pipeline")
