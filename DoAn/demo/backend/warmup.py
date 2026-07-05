from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .models import RetrievalSettings
from .paths import CORPUS_CHUNK_DIR
from .retrieval import build_bm25_state, build_retrieval_state
from .routing import load_sbert_router


def warmup_models(
    settings: RetrievalSettings,
    *,
    chunk_dir: Path = CORPUS_CHUNK_DIR,
    doc_scopes: tuple[str, ...] = (),
) -> dict[str, Any]:
    checks = []
    started = time.perf_counter()

    if settings.router_kind == "sbert":
        t0 = time.perf_counter()
        load_sbert_router(settings.router_model)
        checks.append(
            {
                "name": "router",
                "model": settings.router_label,
                "status": "ok",
                "seconds": round(time.perf_counter() - t0, 2),
            }
        )
    else:
        checks.append(
            {
                "name": "router",
                "model": settings.router_label,
                "status": "skip",
                "seconds": 0.0,
            }
        )

    t0 = time.perf_counter()
    if settings.embedding_model == "none":
        build_bm25_state(str(chunk_dir), doc_scopes)
        checks.append(
            {
                "name": "retrieval",
                "model": "BM25-only",
                "status": "ok",
                "seconds": round(time.perf_counter() - t0, 2),
            }
        )
    else:
        build_retrieval_state(
            str(chunk_dir),
            doc_scopes,
            settings.embedding_model,
            settings.embedding_truncate_dim,
            settings.reranker_model,
        )
        checks.append(
            {
                "name": "retrieval",
                "model": f"{settings.embedding_label} + {settings.reranker_label}",
                "status": "ok",
                "seconds": round(time.perf_counter() - t0, 2),
            }
        )

    return {
        "ready": True,
        "total_seconds": round(time.perf_counter() - started, 2),
        "checks": checks,
    }
