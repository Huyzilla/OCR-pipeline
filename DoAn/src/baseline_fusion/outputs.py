from __future__ import annotations

import csv
from pathlib import Path


CSV_FIELDNAMES = [
    "question_index",
    "question",
    "intent",
    "ground_truth",
    "predicted",
    "is_correct",
    "format_ok",
    "route_ms",
    "retrieve_ms",
    "rerank_ms",
    "extract_ms",
    "reasoning_ms",
    "answer_ms",
    "llm_ms",
    "generation_ms",
    "total_ms",
    "top_chunk_ids",
    "raw_answer",
]


def build_debug_entry(
    pipeline_name: str,
    prep: dict,
    raw_answer: str,
    num_answers: int,
    predicted: str,
    format_ok: bool,
    answer_s: float,
    generation_s: float,
    intent: str | None = None,
    route_s: float = 0.0,
    reasoning: str | None = None,
    reasoning_s: float = 0.0,
    extracted: str | None = None,
    extract_s: float = 0.0,
) -> dict:
    q_item = prep["q_item"]
    top_chunks = prep["top_chunks"]
    chunk_ids = [c["id"] for c in top_chunks]
    doc_ids = list(dict.fromkeys(cid.split("::")[0] for cid in chunk_ids))

    intent = intent or prep.get("intent", "")
    route_s = route_s or prep.get("route_s", 0.0)
    llm_s = extract_s + reasoning_s + answer_s
    pipeline_s = route_s + prep.get("retrieve_s", 0.0) + prep.get("rerank_s", 0.0) + generation_s

    entry = {
        "pipeline_name": pipeline_name,
        "id": q_item["index"],
        "question_index": q_item["index"] + 1,
        "question": q_item["question"],
        "intent": intent,
        "options": {chr(65 + i): opt for i, opt in enumerate(q_item["options"]) if opt},
        "ground_truth": q_item.get("ground_truth"),
        "predicted": predicted,
        "num_answers": num_answers,
        "is_correct": predicted == q_item.get("ground_truth") if q_item.get("ground_truth") else None,
        "detected_pub_ids": prep.get("pub_ids", []),
        "router_public_ids": prep.get("router_public_ids", []),
        "retrieve_mode": prep.get("retrieve_mode"),
        "retrieval": {
            "chunk_ids": chunk_ids,
            "doc_ids": doc_ids,
            "recall_check_text": "\n\n".join(c.get("text", "") for c in top_chunks),
            "top_chunks": [
                {
                    "chunk_id": c["id"],
                    "rerank_score": c.get("rerank_score"),
                    "rrf_score": c.get("score"),
                    "bm25_rank": c.get("bm25_rank"),
                    "dense_rank": c.get("dense_rank"),
                    "text": c.get("text", ""),
                }
                for c in top_chunks
            ],
        },
        "generation": {
            "raw": raw_answer,
            "format_ok": format_ok,
            "reasoning": reasoning or "",
        },
        "performance": {
            "route_ms": round(route_s * 1000, 1),
            "retrieve_ms": round(prep.get("retrieve_s", 0.0) * 1000, 1),
            "rerank_ms": round(prep.get("rerank_s", 0.0) * 1000, 1),
            "extract_ms": round(extract_s * 1000, 1),
            "reasoning_ms": round(reasoning_s * 1000, 1),
            "answer_ms": round(answer_s * 1000, 1),
            "llm_ms": round(llm_s * 1000, 1),
            "generation_ms": round(generation_s * 1000, 1),
            "total_ms": round(pipeline_s * 1000, 1),
            "latency_s": round(pipeline_s, 2),
        },
    }
    if extracted is not None:
        entry["fusion_extracted"] = extracted
    return entry


def open_output_csv(path: Path, resume: bool):
    mode = "a" if resume and path.exists() and path.stat().st_size > 0 else "w"
    if mode == "a":
        with path.open("r", encoding="utf-8-sig", newline="") as existing:
            existing_fields = csv.DictReader(existing).fieldnames or []
        if existing_fields != CSV_FIELDNAMES:
            raise SystemExit(
                f"{path} has an old CSV header. Set RESUME = False in "
                "the baseline runner to recreate it, or choose a different output path."
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    f = path.open(mode, encoding="utf-8", newline="")
    writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
    if mode == "w":
        writer.writeheader()
    return f, writer


def write_output_row(
    writer,
    prep: dict,
    raw: str,
    predicted: str,
    format_ok: bool,
    answer_s: float,
    generation_s: float,
    intent: str | None = None,
    route_s: float = 0.0,
    reasoning_s: float = 0.0,
    extract_s: float = 0.0,
) -> None:
    q_item = prep["q_item"]
    intent = intent or prep.get("intent", "")
    route_s = route_s or prep.get("route_s", 0.0)
    llm_s = extract_s + reasoning_s + answer_s
    pipeline_s = route_s + prep.get("retrieve_s", 0.0) + prep.get("rerank_s", 0.0) + generation_s
    writer.writerow({
        "question_index": q_item["index"] + 1,
        "question": q_item["question"],
        "intent": intent,
        "ground_truth": q_item.get("ground_truth"),
        "predicted": predicted,
        "is_correct": predicted == q_item.get("ground_truth") if q_item.get("ground_truth") else "",
        "format_ok": format_ok,
        "route_ms": round(route_s * 1000, 1),
        "retrieve_ms": round(prep.get("retrieve_s", 0.0) * 1000, 1),
        "rerank_ms": round(prep.get("rerank_s", 0.0) * 1000, 1),
        "extract_ms": round(extract_s * 1000, 1),
        "reasoning_ms": round(reasoning_s * 1000, 1),
        "answer_ms": round(answer_s * 1000, 1),
        "llm_ms": round(llm_s * 1000, 1),
        "generation_ms": round(generation_s * 1000, 1),
        "total_ms": round(pipeline_s * 1000, 1),
        "top_chunk_ids": "|".join(c["id"] for c in prep["top_chunks"]),
        "raw_answer": raw,
    })
