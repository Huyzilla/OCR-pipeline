from __future__ import annotations

from datetime import datetime
from pathlib import Path

from qa.question_io import load_router_questions
from qa.utils import load_all_chunks


def run_qa_pipeline(
    question_csv: Path,
    chunk_dir: Path,
    doc_index_dir: Path,
    output_json: Path | None = None,
    output_csv: Path | None = None,
    max_questions: int = 0,
    router_model: str = "gpt-4o-mini",
    embedding_model: str = "AITeamVN/Vietnamese_Embedding_v2",
    rerank_model: str = "BAAI/bge-reranker-v2-m3",
    answer_model: str = "gpt-4o-mini",
    context_debug: bool = False,
):
    print("\n" + "=" * 70)
    print("QA Pipeline - Router-Summary Approach")
    print("=" * 70)

    start_time = datetime.now()

    all_questions = load_router_questions(question_csv)
    if max_questions > 0:
        questions = all_questions[:max_questions]
        print(f"Processing {len(questions)}/{len(all_questions)} questions")
    else:
        questions = all_questions
        print(f"Processing all {len(questions)} questions")

    print(f"\nLoading chunks from {chunk_dir}...")
    all_chunks = load_all_chunks(chunk_dir)
    print(f"Loaded {len(all_chunks)} chunks")

    print("\nInitializing QA pipeline...")
    from pipeline_router_summary import create_qa_pipeline

    pipeline = create_qa_pipeline(
        all_chunks=all_chunks,
        doc_index_dir=doc_index_dir,
        embedding_model=embedding_model,
        rerank_model=rerank_model,
        router_model=router_model,
        answer_model=answer_model,
    )

    print("\nProcessing questions...")
    results = pipeline.process_batch(
        questions,
        output_json=output_json,
        output_csv=output_csv,
        context_debug=context_debug and len(questions) > 0,
    )

    elapsed = datetime.now() - start_time
    total = len(results)

    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"Total questions: {total}")
    print(f"Time elapsed: {elapsed}")
    if total:
        print(f"Time per question: {elapsed.total_seconds() / total:.1f}s")

    has_truth = sum(1 for r in results if r["truth"] is not None)
    if has_truth > 0:
        correct = sum(1 for r in results if r["is_correct"] is True)
        print(f"Accuracy: {correct}/{has_truth} ({correct / has_truth * 100:.1f}%)")

        by_intent = {}
        for r in results:
            if r["truth"] is None:
                continue
            intent = r["intent"]
            if intent not in by_intent:
                by_intent[intent] = {"total": 0, "correct": 0}
            by_intent[intent]["total"] += 1
            if r["is_correct"]:
                by_intent[intent]["correct"] += 1

        print("\nAccuracy by intent:")
        for intent, stats in by_intent.items():
            if stats["total"] > 0:
                pct = stats["correct"] / stats["total"] * 100
                print(f"  {intent}: {stats['correct']}/{stats['total']} ({pct:.1f}%)")

    print("\nPipeline completed.")
    return results
