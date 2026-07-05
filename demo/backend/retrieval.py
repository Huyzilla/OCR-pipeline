from __future__ import annotations

import time
import pickle
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from .models import RetrievalSettings
from .paths import CORPUS_CHUNK_DIR, PROJECT_ROOT, setup_project_paths

setup_project_paths()

from qa.utils import ChunkRecord, load_all_chunks, tokenize_vi


def _cached_embedding_path(
    chunk_dir_text: str,
    doc_scopes: tuple[str, ...],
    embedding_model: str,
    embedding_truncate_dim: int | None,
) -> Path | None:
    if doc_scopes:
        return None
    try:
        if Path(chunk_dir_text).resolve() != CORPUS_CHUNK_DIR.resolve():
            return None
    except OSError:
        return None

    model_text = embedding_model.replace("\\", "/").lower()
    cache_dir = PROJECT_ROOT / "cache"
    if "embed_gist_mnr" in model_text and embedding_truncate_dim == 512:
        return cache_dir / "cache_chunk_embeddings_embed_gist_mnr_512d_chunks1.pkl"
    if "vietnamese_embedding_v2" in model_text and embedding_truncate_dim is None:
        return cache_dir / "cache_chunk_embeddings_vn_embed_v2_chunks1.pkl"
    return None


def _load_cached_embeddings(cache_path: Path | None, expected_rows: int) -> np.ndarray | None:
    if cache_path is None or not cache_path.exists():
        return None
    with cache_path.open("rb") as f:
        embeddings = pickle.load(f)
    embeddings = np.asarray(embeddings)
    if embeddings.ndim == 2 and embeddings.shape[0] == expected_rows:
        print(f"Loaded cached chunk embeddings: {cache_path}")
        return embeddings
    print(f"Skip embedding cache with unexpected shape: {cache_path} {embeddings.shape}")
    return None


@lru_cache(maxsize=16)
def load_records(chunk_dir_text: str, doc_scopes: tuple[str, ...] = ()) -> tuple[ChunkRecord, ...]:
    records = load_all_chunks(Path(chunk_dir_text))
    if doc_scopes:
        allowed = set(doc_scopes)
        records = [record for record in records if record.doc_scope in allowed]
    return tuple(records)


@lru_cache(maxsize=8)
def build_retrieval_state(
    chunk_dir_text: str,
    doc_scopes: tuple[str, ...],
    embedding_model: str,
    embedding_truncate_dim: int | None,
    reranker_model: str,
) -> dict[str, Any]:
    from rank_bm25 import BM25Okapi
    from sentence_transformers import CrossEncoder, SentenceTransformer
    import torch

    records = list(load_records(chunk_dir_text, doc_scopes))
    texts = [record.text for record in records]
    if not texts:
        raise RuntimeError("Không tìm thấy dữ liệu phù hợp để truy hồi.")

    bm25 = BM25Okapi([tokenize_vi(text) for text in texts])
    embedder = SentenceTransformer(embedding_model, truncate_dim=embedding_truncate_dim)
    embeddings = _load_cached_embeddings(
        _cached_embedding_path(
            chunk_dir_text,
            doc_scopes,
            embedding_model,
            embedding_truncate_dim,
        ),
        expected_rows=len(texts),
    )
    if embeddings is None:
        embeddings = embedder.encode(
            texts,
            batch_size=64,
            show_progress_bar=False,
            normalize_embeddings=True,
            truncate_dim=embedding_truncate_dim,
        )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    reranker = None
    if reranker_model and reranker_model != "none":
        reranker = CrossEncoder(reranker_model, device=device)

    return {
        "records": records,
        "texts": texts,
        "bm25": bm25,
        "embedder": embedder,
        "embeddings": np.asarray(embeddings),
        "reranker": reranker,
    }


@lru_cache(maxsize=8)
def build_bm25_state(chunk_dir_text: str, doc_scopes: tuple[str, ...]) -> dict[str, Any]:
    from rank_bm25 import BM25Okapi

    records = list(load_records(chunk_dir_text, doc_scopes))
    texts = [record.text for record in records]
    if not texts:
        raise RuntimeError("Không tìm thấy dữ liệu phù hợp để truy hồi.")

    return {
        "records": records,
        "texts": texts,
        "bm25": BM25Okapi([tokenize_vi(text) for text in texts]),
    }


def retrieve_chunks(
    question: str,
    state: dict[str, Any],
    settings: RetrievalSettings,
) -> tuple[list[dict[str, Any]], dict[str, float]]:
    t0 = time.perf_counter()
    query_embedding = state["embedder"].encode(
        [question],
        show_progress_bar=False,
        normalize_embeddings=True,
        truncate_dim=settings.embedding_truncate_dim,
    )[0]

    texts = state["texts"]
    records = state["records"]
    n_items = len(texts)
    dense_k = min(settings.dense_top_k, n_items)
    bm25_k = min(settings.bm25_top_k, n_items)

    dense_scores = np.matmul(state["embeddings"], query_embedding)
    dense_top_idx = np.argsort(dense_scores)[-dense_k:][::-1].tolist()

    bm25_scores = state["bm25"].get_scores(tokenize_vi(question))
    bm25_top_idx = np.argsort(bm25_scores)[-bm25_k:][::-1].tolist()

    rrf_scores: dict[int, float] = {}
    dense_rank: dict[int, int] = {}
    bm25_rank: dict[int, int] = {}
    k_rrf = 60

    for rank, idx in enumerate(bm25_top_idx, start=1):
        rrf_scores[idx] = rrf_scores.get(idx, 0.0) + 1.0 / (k_rrf + rank)
        bm25_rank[idx] = rank

    for rank, idx in enumerate(dense_top_idx, start=1):
        rrf_scores[idx] = rrf_scores.get(idx, 0.0) + 1.0 / (k_rrf + rank)
        dense_rank[idx] = rank

    candidates = []
    for idx in sorted(rrf_scores, key=lambda item: rrf_scores[item], reverse=True):
        record = records[idx]
        candidates.append(
            {
                "id": record.chunk_id,
                "doc": record.doc_scope,
                "text": record.text,
                "source_file": record.source_file,
                "section_hint": record.section_hint,
                "chunk_index": record.chunk_index,
                "rrf_score": float(rrf_scores[idx]),
                "dense_rank": dense_rank.get(idx),
                "dense_score": float(dense_scores[idx]),
                "bm25_rank": bm25_rank.get(idx),
                "bm25_score": float(bm25_scores[idx]),
            }
        )
    retrieve_s = time.perf_counter() - t0

    t1 = time.perf_counter()
    if candidates and state.get("reranker") is not None:
        pairs = [(question, candidate["text"]) for candidate in candidates]
        scores = state["reranker"].predict(pairs)
        for candidate, score in zip(candidates, scores):
            candidate["rerank_score"] = float(score)
        candidates.sort(key=lambda item: item["rerank_score"], reverse=True)
    else:
        for candidate in candidates:
            candidate["rerank_score"] = 0.0
    rerank_s = time.perf_counter() - t1

    return candidates[: settings.final_top_k], {
        "retrieve_s": retrieve_s,
        "rerank_s": rerank_s,
    }


def retrieve_bm25_chunks(
    question: str,
    state: dict[str, Any],
    top_k: int,
) -> tuple[list[dict[str, Any]], dict[str, float]]:
    t0 = time.perf_counter()
    records = state["records"]
    scores = state["bm25"].get_scores(tokenize_vi(question))
    n_items = len(records)
    selected = np.argsort(scores)[-min(top_k, n_items):][::-1].tolist()

    chunks = []
    for rank, idx in enumerate(selected, start=1):
        record = records[idx]
        chunks.append(
            {
                "id": record.chunk_id,
                "doc": record.doc_scope,
                "text": record.text,
                "source_file": record.source_file,
                "section_hint": record.section_hint,
                "chunk_index": record.chunk_index,
                "rrf_score": 0.0,
                "dense_rank": None,
                "dense_score": None,
                "bm25_rank": rank,
                "bm25_score": float(scores[idx]),
                "rerank_score": 0.0,
            }
        )

    return chunks, {
        "retrieve_s": time.perf_counter() - t0,
        "rerank_s": 0.0,
    }


def build_context(chunks: list[dict[str, Any]]) -> str:
    parts = []
    for idx, chunk in enumerate(chunks, start=1):
        parts.append(f"[Nguồn {idx}: {chunk['doc']} | {chunk['id']}]\n{chunk['text']}")
    return "\n\n---\n\n".join(parts)


def clear_retrieval_cache() -> None:
    load_records.cache_clear()
    build_retrieval_state.cache_clear()
    build_bm25_state.cache_clear()
