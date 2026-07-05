from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .documents import list_ocr_documents, prepare_uploaded_document
from .llm import answer_with_llm
from .models import RetrievalSettings
from .paths import CORPUS_CHUNK_DIR, ensure_runtime_dirs
from .retrieval import (
    build_bm25_state,
    build_context,
    build_retrieval_state,
    clear_retrieval_cache,
    retrieve_bm25_chunks,
    retrieve_chunks,
)
from .routing import route_question
from .routing import clean_question_text


def _is_torch_dll_error(exc: BaseException) -> bool:
    text = str(exc).lower()
    return (
        "c10.dll" in text
        or "winerror 1114" in text
        or "dll initialization routine failed" in text
        or "dynamic link library" in text
    )


def get_corpus_summary() -> dict[str, Any]:
    docs = list_ocr_documents()
    return {
        "documents": docs,
        "document_count": len(docs),
        "chunk_ready": CORPUS_CHUNK_DIR.exists(),
    }


def ask_question(
    question: str,
    settings: RetrievalSettings,
    *,
    chunk_dir: Path = CORPUS_CHUNK_DIR,
    doc_scopes: tuple[str, ...] = (),
) -> dict[str, Any]:
    if not question.strip():
        raise ValueError("Vui lòng nhập câu hỏi.")
    question = clean_question_text(question)

    t0 = time.perf_counter()
    warnings = []

    try:
        intent, route_s = route_question(question, settings)
    except Exception as exc:
        if not _is_torch_dll_error(exc):
            raise
        intent, route_s = "tra_cuu", 0.0
        warnings.append(
            "Không load được router dùng torch, đã chuyển intent mặc định sang tra_cuu."
        )

    retrieval_mode = "hybrid_dense_bm25_rerank"
    if settings.embedding_model == "none":
        retrieval_mode = "bm25_only"
        state = build_bm25_state(str(chunk_dir), doc_scopes)
        chunks, retrieve_timing = retrieve_bm25_chunks(
            question,
            state,
            top_k=settings.final_top_k,
        )
    else:
        try:
            state = build_retrieval_state(
                str(chunk_dir),
                doc_scopes,
                settings.embedding_model,
                settings.embedding_truncate_dim,
                settings.reranker_model,
            )
            chunks, retrieve_timing = retrieve_chunks(question, state, settings)
        except Exception as exc:
            if not _is_torch_dll_error(exc):
                raise
            retrieval_mode = "bm25_only_fallback"
            warnings.append(
                "Không load được embedding/reranker dùng torch, đã dùng BM25-only trên dữ liệu OCR có sẵn."
            )
            state = build_bm25_state(str(chunk_dir), doc_scopes)
            chunks, retrieve_timing = retrieve_bm25_chunks(
                question,
                state,
                top_k=settings.final_top_k,
            )

    context = build_context(chunks)
    answer, answer_s = answer_with_llm(question, context, intent, settings)
    if not answer:
        warnings.append(
            "LLM không trả về nội dung. Kiểm tra OPENAI_API_KEY, quota hoặc log worker."
        )

    return {
        "answer": answer,
        "intent": intent,
        "retrieval_mode": retrieval_mode,
        "warnings": warnings,
        "chunks": chunks,
        "timing": {
            "route_s": route_s,
            **retrieve_timing,
            "answer_s": answer_s,
            "total_s": time.perf_counter() - t0,
        },
        "models": {
            "embedding": settings.embedding_label,
            "reranker": settings.reranker_label,
            "router": settings.router_label,
            "answer": settings.answer_model,
        },
    }


def ask_corpus(question: str, settings: RetrievalSettings) -> dict[str, Any]:
    return ask_question(question, settings, chunk_dir=CORPUS_CHUNK_DIR, doc_scopes=())


def ask_document(question: str, document_info: dict[str, Any], settings: RetrievalSettings) -> dict[str, Any]:
    return ask_question(
        question,
        settings,
        chunk_dir=Path(document_info["chunk_dir"]),
        doc_scopes=(str(document_info["doc_id"]),),
    )


def prepare_user_document(file_name: str, data: bytes, table_format: str = "html") -> dict[str, Any]:
    ensure_runtime_dirs()
    return prepare_uploaded_document(file_name, data, table_format=table_format)


def clear_demo_cache() -> None:
    clear_retrieval_cache()
