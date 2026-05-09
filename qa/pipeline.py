from __future__ import annotations

import csv
from pathlib import Path

from .llm import QwenAnswerer
from .retrieval import HybridQAPipeline
from .tracing import OpikTracer
from .utils import ChunkRecord, detect_public_doc_ids, load_all_chunks, load_doc_chunks, save_mismatch_questions


def run_qa_evaluation(
    question_csv: Path,
    chunk_dir: Path,
    output_file: Path,
    max_questions: int,
    embedding_model: str,
    rerank_model: str,
    cache_dir: Path,
    use_cache: bool,
    llm_model: str,
    use_llm: bool,
    llm_max_new_tokens: int,
    neighbor_hops: int,
    opik_trace: bool,
    opik_project: str,
    opik_use_local: bool,
    truth_file: Path | None,
    mismatch_output: Path,
    context_debug_output: Path | None,
) -> None:
    print("Preparing QA pipelines...")
    global_chunks: list[ChunkRecord] | None = None
    global_qa: HybridQAPipeline | None = None
    doc_qas: dict[str, HybridQAPipeline] = {}

    def ensure_global_qa() -> tuple[HybridQAPipeline, list[ChunkRecord]]:
        nonlocal global_chunks, global_qa
        if global_qa is None or global_chunks is None:
            print("Loading global chunks for fallback...")
            global_chunks = load_all_chunks(chunk_dir)
            if not global_chunks:
                raise RuntimeError("No chunks found in chunk directory")
            print(f"Loaded {len(global_chunks)} global chunks")
            global_qa = HybridQAPipeline(
                chunks=global_chunks,
                embedding_model=embedding_model,
                rerank_model=rerank_model,
                cache_dir=cache_dir / "global",
                use_cache=use_cache,
                neighbor_hops=neighbor_hops,
            )
        return global_qa, global_chunks

    def ensure_doc_qa(doc_id: str) -> tuple[HybridQAPipeline | None, list[ChunkRecord]]:
        if doc_id in doc_qas:
            return doc_qas[doc_id], doc_qas[doc_id].chunks

        doc_chunks = load_doc_chunks(chunk_dir, doc_id)
        if not doc_chunks:
            return None, []

        print(f"Loaded {len(doc_chunks)} chunks for {doc_id}")
        doc_qa = HybridQAPipeline(
            chunks=doc_chunks,
            embedding_model=embedding_model,
            rerank_model=rerank_model,
            cache_dir=cache_dir / doc_id,
            use_cache=use_cache,
            neighbor_hops=neighbor_hops,
        )
        doc_qas[doc_id] = doc_qa
        return doc_qa, doc_chunks

    llm_answerer = QwenAnswerer(llm_model, max_new_tokens=llm_max_new_tokens) if use_llm else None
    tracer = OpikTracer(enabled=opik_trace, project_name=opik_project, use_local=opik_use_local)

    results: list[str] = []
    context_debug_lines: list[str] = []
    with question_csv.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            if max_questions > 0 and idx > max_questions:
                break

            question = row.get("Question", "").strip()
            if not question:
                continue

            options = {
                "A": row.get("A", "").strip(),
                "B": row.get("B", "").strip(),
                "C": row.get("C", "").strip(),
                "D": row.get("D", "").strip(),
            }

            candidate_doc_ids = detect_public_doc_ids(question)

            active_qa: HybridQAPipeline
            active_chunks: list[ChunkRecord]
            route_tag = "global"

            if len(candidate_doc_ids) == 1:
                doc_id = candidate_doc_ids[0]
                doc_qa, doc_texts = ensure_doc_qa(doc_id)
                if doc_qa is not None:
                    active_qa = doc_qa
                    active_chunks = doc_texts
                    route_tag = doc_id
                else:
                    active_qa, active_chunks = ensure_global_qa()
            else:
                active_qa, active_chunks = ensure_global_qa()

            # Some Windows terminals use cp1252; replace unsupported chars to avoid hard crash.
            question_preview = question[:80].encode("cp1252", errors="replace").decode("cp1252")
            print(f"[{idx}][{route_tag}] {question_preview}...")

            trace_obj = tracer.start_trace(
                name="qa_question",
                input_data={"question": question, "options": options},
                metadata={
                    "question_index": idx,
                    "route": route_tag,
                    "doc_candidates": candidate_doc_ids,
                    "llm_enabled": bool(llm_answerer is not None and llm_answerer.enabled),
                },
            )

            retrieval_span = tracer.start_span(
                trace_obj,
                name="hybrid_retrieval",
                span_type="tool",
                input_data={"question": question},
                metadata={"route": route_tag},
            )
            seed_chunk_ids, expanded_chunk_ids, scored_chunks = active_qa.retrieve_with_scored_details(question)
            retrieved_contexts = [active_chunks[i].text for i in expanded_chunk_ids]
            compact_scored_chunks = [
                {
                    "chunk_id": item.get("chunk_id"),
                    "doc_scope": item.get("doc_scope"),
                    "text": active_chunks[int(item["chunk_index"])] .text if item.get("chunk_index") is not None else "",
                    "rerank_score": item.get("rerank_score"),
                }
                for item in scored_chunks
            ]
            tracer.update(
                retrieval_span,
                output_data={
                    "seed_chunk_indices": seed_chunk_ids,
                    "expanded_chunk_indices": expanded_chunk_ids,
                    "seed_chunk_ids": [active_chunks[i].chunk_id for i in seed_chunk_ids],
                    "expanded_chunk_ids": [active_chunks[i].chunk_id for i in expanded_chunk_ids],
                    "expanded_chunk_scores": compact_scored_chunks,
                    "top_context_preview": [c[:400] for c in retrieved_contexts[:3]],
                },
            )
            tracer.end(retrieval_span)

            answers: list[str] = []
            answer_source = "fallback"
            fallback_reason = "llm_disabled"
            llm_raw_output = ""
            if llm_answerer is not None and llm_answerer.enabled:
                fallback_reason = "llm_empty"
                llm_span = tracer.start_span(
                    trace_obj,
                    name="llm_answer",
                    span_type="llm",
                    input_data={"question": question, "route": route_tag},
                    metadata={"model": llm_model},
                )
                try:
                    answers = llm_answerer.answer(question, options, retrieved_contexts)
                    llm_raw_output = str(llm_answerer.last_debug.get("raw_output", ""))
                    if answers:
                        answer_source = "llm"
                        fallback_reason = None
                except Exception as e:
                    answers = []
                    fallback_reason = f"llm_error:{type(e).__name__}"
                tracer.update(
                    llm_span,
                    output_data={
                        "parsed_answers": answers,
                        "llm_raw_output": llm_raw_output,
                        "llm_error": fallback_reason if fallback_reason and fallback_reason.startswith("llm_error:") else None,
                        "answer_source": "llm" if answers else "fallback",
                    },
                    metadata={
                        "context_chars": llm_answerer.last_debug.get("context_chars", 0),
                        "prompt_chars": len(llm_answerer.last_debug.get("system_prompt", ""))
                        + len(llm_answerer.last_debug.get("user_prompt", "")),
                    },
                )
                tracer.end(llm_span)

            if not answers:
                answers = active_qa.choose_answers(question, options, expanded_chunk_ids)
                answer_source = "fallback"
                if llm_answerer is not None and llm_answerer.enabled:
                    fallback_reason = "llm_empty"
                else:
                    fallback_reason = "llm_disabled"

            num_corrects = len(answers)
            if answers:
                answer_text = ",".join(answers)
                if len(answers) > 1:
                    answer_text = f'"{answer_text}"'
            else:
                answer_text = "?"
            results.append(f"{num_corrects},{answer_text}")

            tracer.update(
                trace_obj,
                output_data={
                    "num_corrects": num_corrects,
                    "answers": answers,
                    "answer_source": answer_source,
                    "used_llm": answer_source == "llm",
                    "used_fallback": answer_source == "fallback",
                    "fallback_reason": fallback_reason,
                    "formatted": f"{num_corrects},{answer_text}",
                },
            )
            tracer.end(trace_obj)

            if context_debug_output is not None:
                context_debug_lines.append(f"## Q{idx}")
                context_debug_lines.append(f"- route: {route_tag}")
                context_debug_lines.append(f"- answer_source: {answer_source}")
                context_debug_lines.append(f"- fallback_reason: {fallback_reason}")
                context_debug_lines.append(f"- result: {num_corrects},{answer_text}")
                raw_output_preview = llm_raw_output.replace("\n", " ").strip()
                if not raw_output_preview:
                    raw_output_preview = "<empty>"
                elif len(raw_output_preview) > 800:
                    raw_output_preview = raw_output_preview[:800] + "..."
                context_debug_lines.append(f"- llm_raw_output: {raw_output_preview}")
                context_debug_lines.append(f"- seed_chunk_ids: {[active_chunks[i].chunk_id for i in seed_chunk_ids]}")
                context_debug_lines.append(f"- expanded_chunk_ids: {[active_chunks[i].chunk_id for i in expanded_chunk_ids]}")
                context_debug_lines.append("- contexts:")
                for i, item in enumerate(compact_scored_chunks, start=1):
                    chunk_id = item.get("chunk_id", "")
                    doc_scope = item.get("doc_scope", "")
                    rerank_score = item.get("rerank_score", None)
                    text = str(item.get("text", "")).replace("\n", " ")
                    if len(text) > 500:
                        text = text[:500] + "..."
                    context_debug_lines.append(
                        f"  - [{i}] chunk_id={chunk_id} | doc_scope={doc_scope} | rerank_score={rerank_score} | text={text}"
                    )
                context_debug_lines.append("")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        for line in results:
            f.write(line + "\n")

    print(f"Saved {len(results)} lines to {output_file}")

    if context_debug_output is not None:
        context_debug_output.parent.mkdir(parents=True, exist_ok=True)
        with context_debug_output.open("w", encoding="utf-8") as f:
            f.write("# Retrieval Context Debug\n\n")
            for line in context_debug_lines:
                f.write(line + "\n")
        print(f"Saved context debug to {context_debug_output}")

    if truth_file is not None:
        mismatch_count = save_mismatch_questions(results, truth_file, mismatch_output)
        print(f"Saved mismatch report to {mismatch_output} (mismatches={mismatch_count})")
