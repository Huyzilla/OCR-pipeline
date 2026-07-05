import json
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, TypedDict
from tqdm import tqdm

from .router import QuestionRouter, RouterResult
from .doc_indexer import DocIndexer
from .multi_doc_retrieval import MultiDocPipeline, RetrievedChunk
from .answer_generator import AnswerGenerator, AnswerResult

try:
    from qa.utils import ChunkRecord
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from qa.utils import ChunkRecord


class QAPipelineInput(TypedDict):
    question: str
    options:  Optional[dict]
    truth:    Optional[str]


class QAPipelineOutput(TypedDict):
    question:         str
    intent:           str
    public_ids:       list[str]
    selected_docs:    list[str]
    retrieve_mode:    str           # "direct" | "doc_index"
    context:          str
    answer:           str
    reasoning:        str
    truth:            Optional[str]
    is_correct:       Optional[bool]
    retrieved_chunks: list[dict]
    timestamp:        str


class RouterSummaryQAPipeline:
    def __init__(
        self,
        all_chunks:      list[ChunkRecord],
        doc_index_dir:   Path,
        embedding_model: str = "AITeamVN/Vietnamese_Embedding_v2",
        rerank_model:    str = "BAAI/bge-reranker-v2-m3",
        router_model:    str = "gpt-4o-mini",
        answer_model:    str = "gpt-4o-mini",
        chunk_emb_cache: Optional[Path] = Path("cache/cache_chunk_embeddings.pkl"),
    ):
        print("=" * 60)
        print("Initializing RouterSummaryQAPipeline")
        print("=" * 60)

        print("\n[1/4] Router (GPT intent + regex public_id)...")
        self.router = QuestionRouter(model_name=router_model)

        print("\n[2/4] DocIndexer (load offline index)...")
        self.doc_indexer = DocIndexer(Path(doc_index_dir))

        print("\n[3/4] MultiDocPipeline (hybrid chunk retrieve + BGE rerank)...")
        self.multi_doc_pipeline = MultiDocPipeline(
            doc_indexer     = self.doc_indexer,
            all_chunks      = all_chunks,
            embedding_model = embedding_model,
            rerank_model    = rerank_model,
            chunk_emb_cache = chunk_emb_cache,
        )

        print("\n[4/4] AnswerGenerator (GPT-4o-mini)...")
        self.answer_generator = AnswerGenerator(model_name=answer_model)

        print("\n" + "=" * 60)
        print("Pipeline ready!")
        print("=" * 60)

    def process_question(
        self,
        question:      str,
        options:       Optional[dict] = None,
        truth:         Optional[str]  = None,
        context_debug: bool           = False,
    ) -> QAPipelineOutput:

        output: QAPipelineOutput = {
            "question":         question,
            "intent":           "",
            "public_ids":       [],
            "selected_docs":    [],
            "retrieve_mode":    "",
            "context":          "",
            "answer":           "",
            "reasoning":        "",
            "truth":            truth,
            "is_correct":       None,
            "retrieved_chunks": [],
            "timestamp":        datetime.now().isoformat(),
        }

        # Step 1: Router
        print(f"\n[Router] {question[:70]}...")
        router_result: RouterResult = self.router.route(question)
        output["intent"]     = router_result["intent"]
        output["public_ids"] = router_result["public_ids"]
        print(f"  intent={router_result['intent']}  public_ids={router_result['public_ids']}")

        # Step 2: Doc scope → retrieve
        print(f"\n[Retrieval]")
        retrieved_chunks, selected_docs = self.multi_doc_pipeline.retrieve_for_question(
            question   = question,
            public_ids = router_result["public_ids"],
        )
        output["selected_docs"] = selected_docs
        output["retrieve_mode"] = "direct" if router_result["public_ids"] else "doc_index"

        if not retrieved_chunks:
            print("  ⚠ No chunks retrieved!")
            return output

        n_docs = len({c["doc_id"] for c in retrieved_chunks})
        print(f"  Retrieved {len(retrieved_chunks)} chunks from {n_docs} doc(s)")

        context = "\n\n".join(c["text"] for c in retrieved_chunks)
        output["context"] = context
        output["retrieved_chunks"] = [
            {
                "rank":         i + 1,
                "chunk_id":     c["chunk_id"],
                "doc_id":       c["doc_id"],
                "rerank_score": c.get("rerank_score"),
                "rrf_score":    c.get("score"),
                "text_preview": c["text"][:300],
                "text_full":    c["text"],
            }
            for i, c in enumerate(retrieved_chunks)
        ]

        if context_debug:
            print(f"  Context length: {len(context)} chars")
            for i, c in enumerate(retrieved_chunks[:3]):
                print(f"  [{i+1}] {c['chunk_id']} | rerank={c['rerank_score']:.3f}")
                print(f"       {c['text'][:100]}...")

        # Step 3: Answer
        print(f"\n[Answer] intent={router_result['intent']}")
        answer_result: AnswerResult = self.answer_generator.generate_answer(
            context  = context,
            question = question,
            intent   = router_result["intent"],
            options  = options,
        )
        output["answer"]    = answer_result["answer"]
        output["reasoning"] = answer_result["reasoning"]
        print(f"  → {answer_result['answer']}")

        if truth:
            output["is_correct"] = (
                answer_result["answer"].strip().upper() == truth.strip().upper()
            )
            print(f"  correct={output['is_correct']} (truth={truth})")

        return output

    def process_batch(
        self,
        questions:     list[QAPipelineInput],
        output_json:   Optional[Path] = None,
        output_csv:    Optional[Path] = None,
        context_debug: bool           = False,
    ) -> list[QAPipelineOutput]:

        print(f"\n{'='*60}")
        print(f"Processing {len(questions)} questions")
        print(f"{'='*60}")

        results: list[QAPipelineOutput] = []
        start_idx = 0

        # Resume logic: if output_json exists, load it; else if output_csv exists, count lines
        if output_json and os.path.exists(output_json):
            try:
                with open(output_json, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                if isinstance(existing, list) and len(existing) > 0:
                    results = existing
                    start_idx = len(results)
                    print(f"✓ Loaded existing JSON: {start_idx} questions already processed")
            except Exception as e:
                print(f"⚠ Could not load JSON: {e}")
                start_idx = 0
        elif output_csv and os.path.exists(output_csv):
            try:
                with open(output_csv, "r", encoding="utf-8", newline="") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                n_rows = len(rows)
                if n_rows > 0:
                    # Detect header: check if first row looks like header
                    header_like = False
                    if rows and rows[0]:
                        first_cell = rows[0][0].lower() if rows[0][0] else ""
                        if any(x in first_cell for x in ["question", "answer", "result", "id", "index"]):
                            header_like = True
                    start_idx = n_rows - (1 if header_like else 0)
                    print(f"✓ Found existing CSV: {start_idx} questions already processed")
            except Exception as e:
                print(f"⚠ Could not read CSV: {e}")
                start_idx = 0

        for i, q_input in enumerate(tqdm(questions, desc="QA Pipeline"), 1):
            if i <= start_idx:
                continue
            print(f"\n── Q{i}/{len(questions)} ──")
            result = self.process_question(
                question      = q_input["question"],
                options       = q_input.get("options"),
                truth         = q_input.get("truth"),
                context_debug = context_debug and i == 1,
            )
            results.append(result)

            # Incremental save — JSON (đủ thông tin debug, không cần file riêng)
            if output_json:
                output_json.parent.mkdir(parents=True, exist_ok=True)
                with open(output_json, "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)

            # Incremental save — CSV
            if output_csv:
                output_csv.parent.mkdir(parents=True, exist_ok=True)
                with open(output_csv, "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    for r in results:
                        ans   = r.get("answer", "")
                        parts = [p.strip() for p in ans.split(",") if p.strip()]
                        if not parts:
                            writer.writerow([0, "X"])
                        elif len(parts) == 1:
                            writer.writerow([1, parts[0]])
                        else:
                            writer.writerow([len(parts), ",".join(parts)])

        if output_json:
            print(f"\n✓ JSON → {output_json}")
        if output_csv:
            print(f"✓ CSV  → {output_csv}")

        # Summary
        total     = len(results)
        has_truth = sum(1 for r in results if r["truth"] is not None)
        correct   = sum(1 for r in results if r["is_correct"] is True)

        intent_counts: dict[str, int] = {}
        mode_counts:   dict[str, int] = {}
        for r in results:
            intent_counts[r["intent"]]      = intent_counts.get(r["intent"], 0) + 1
            mode_counts[r["retrieve_mode"] or "empty"] = mode_counts.get(r["retrieve_mode"] or "empty", 0) + 1

        print(f"\n{'='*60}")
        print(f"Total: {total}")
        if has_truth:
            print(f"Accuracy: {correct}/{has_truth} ({correct/has_truth*100:.1f}%)")
        print(f"Intent:   {intent_counts}")
        print(f"Retrieve: {mode_counts}")
        print(f"{'='*60}")

        return results


def create_qa_pipeline(
    all_chunks:      list[ChunkRecord],
    doc_index_dir:   Path = Path("doc_index"),
    embedding_model: str  = "AITeamVN/Vietnamese_Embedding_v2",
    rerank_model:    str  = "BAAI/bge-reranker-v2-m3",
    router_model:    str  = "gpt-4o-mini",
    answer_model:    str  = "gpt-4o-mini",
    chunk_emb_cache: Optional[Path] = Path("cache/cache_chunk_embeddings.pkl"),
) -> RouterSummaryQAPipeline:
    return RouterSummaryQAPipeline(
        all_chunks      = all_chunks,
        doc_index_dir   = doc_index_dir,
        embedding_model = embedding_model,
        rerank_model    = rerank_model,
        router_model    = router_model,
        answer_model    = answer_model,
        chunk_emb_cache = chunk_emb_cache,
    )


if __name__ == "__main__":
    print("Router-DocIndex QA Pipeline")
    print("Use create_qa_pipeline() to initialize")
