#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-document retrieval: Hybrid retrieval trong top-2 documents với BGE rerank.
Dùng DocIndexer (BM25 + TextRank embedding) thay SummaryIndexer.
"""

import pickle
import re
from pathlib import Path
from typing import Optional, TypedDict

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer

from .doc_indexer import DocIndexer

try:
    from qa.utils import ChunkRecord
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from qa.utils import ChunkRecord


class RetrievedChunk(TypedDict):
    chunk_id:     str
    text:         str
    doc_id:       str
    score:        float
    rerank_score: float


class MultiDocRetriever:
    """
    Hybrid retrieval (BM25 + dense) trong tập chunks của selected docs → BGE rerank.
    """

    def __init__(
        self,
        embedding_model: str = "AITeamVN/Vietnamese_Embedding_v2",
        rerank_model:    str = "BAAI/bge-reranker-v2-m3",
        chunks_per_doc:  int = 5,
        final_top_k:     int = 5,
    ):
        print("Loading embedding model...")
        self.embedder = SentenceTransformer(embedding_model)

        print("Loading rerank model...")
        self.reranker = CrossEncoder(rerank_model)

        self.chunks_per_doc = chunks_per_doc
        self.final_top_k    = final_top_k
        self.bm25_top_k     = chunks_per_doc + 2
        self.dense_top_k    = chunks_per_doc + 2

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        clean = re.sub(r"[^\w\s]", " ", text.lower())
        return [t for t in clean.split() if len(t) > 1]

    def _hybrid_retrieve_from_doc(
        self,
        chunks:    list[ChunkRecord],
        query:     str,
        doc_id:    str,
        query_emb: np.ndarray,          # encode 1 lần từ retrieve_from_documents, truyền xuống
    ) -> list[RetrievedChunk]:
        if not chunks:
            return []

        chunk_texts = [c.text for c in chunks]

        # BM25
        bm25        = BM25Okapi([self._tokenize(t) for t in chunk_texts])
        bm25_scores = bm25.get_scores(self._tokenize(query))
        bm25_top    = np.argsort(bm25_scores)[-self.bm25_top_k:][::-1]

        # Dense — dùng query_emb đã encode sẵn
        cached_chunk_embs = getattr(self, "_cached_chunk_embs", None)
        if cached_chunk_embs is None:
            chunk_embs = self.embedder.encode(chunk_texts, normalize_embeddings=True)
        else:
            chunk_embs = np.asarray(cached_chunk_embs)
            norms = np.linalg.norm(chunk_embs, axis=1, keepdims=True)
            chunk_embs = chunk_embs / np.maximum(norms, 1e-12)
        dense_scores = chunk_embs @ query_emb
        dense_top    = np.argsort(dense_scores)[-self.dense_top_k:][::-1]

        # RRF
        k_rrf = 60
        rrf: dict[int, float] = {}
        for rank, idx in enumerate(bm25_top):
            rrf[idx] = rrf.get(idx, 0.0) + 1.0 / (k_rrf + rank + 1)
        for rank, idx in enumerate(dense_top):
            rrf[idx] = rrf.get(idx, 0.0) + 1.0 / (k_rrf + rank + 1)

        top_idx = sorted(rrf, key=lambda x: rrf[x], reverse=True)[:self.chunks_per_doc]

        return [
            {
                "chunk_id":     chunks[i].chunk_id,
                "text":         chunks[i].text,
                "doc_id":       doc_id,
                "score":        rrf[i],
                "rerank_score": 0.0,
            }
            for i in top_idx
        ]

    def retrieve_from_documents(
        self,
        query:          str,
        doc_chunks_map: dict[str, list[ChunkRecord]],
    ) -> list[RetrievedChunk]:
        # Encode query 1 lần duy nhất, tái sử dụng cho tất cả docs
        query_emb = self.embedder.encode(query, normalize_embeddings=True)

        all_retrieved: list[RetrievedChunk] = []
        for doc_id, chunks in doc_chunks_map.items():
            all_retrieved.extend(
                self._hybrid_retrieve_from_doc(chunks, query, doc_id, query_emb)
            )

        if all_retrieved:
            scores = self.reranker.predict([(query, c["text"]) for c in all_retrieved])
            for c, s in zip(all_retrieved, scores):
                c["rerank_score"] = float(s)

        all_retrieved.sort(key=lambda x: x["rerank_score"], reverse=True)
        return all_retrieved[:self.final_top_k]


class MultiDocPipeline:
    """
    Pipeline: DocIndexer doc search → chunk-level hybrid retrieve → rerank.
    """

    def __init__(
        self,
        doc_indexer:     DocIndexer,
        all_chunks:      list[ChunkRecord],
        embedding_model: str = "AITeamVN/Vietnamese_Embedding_v2",
        rerank_model:    str = "BAAI/bge-reranker-v2-m3",
        chunk_emb_cache: Optional[Path] = Path("cache/cache_chunk_embeddings.pkl"),
    ):
        self.doc_indexer = doc_indexer
        self.retriever   = MultiDocRetriever(embedding_model, rerank_model)
        self.chunk_embedding_map = self._load_chunk_embedding_map(
            all_chunks, chunk_emb_cache
        )

        # Build chunk_map: doc_id → [ChunkRecord]
        self.chunk_map: dict[str, list[ChunkRecord]] = {}
        for chunk in all_chunks:
            doc_id = chunk.chunk_id.split("::")[0]
            self.chunk_map.setdefault(doc_id, []).append(chunk)

    def _load_chunk_embedding_map(
        self,
        all_chunks: list[ChunkRecord],
        chunk_emb_cache: Optional[Path],
    ) -> dict[str, np.ndarray] | None:
        if chunk_emb_cache is None:
            print("Chunk embedding cache disabled; encoding selected chunks per query.")
            return None

        cache_path = Path(chunk_emb_cache)
        if not cache_path.exists():
            print(f"Chunk embedding cache not found: {cache_path}. Falling back to per-query encode.")
            return None

        try:
            with cache_path.open("rb") as f:
                cached = pickle.load(f)
            embs = np.asarray(cached)
        except Exception as exc:
            print(f"Could not load chunk embedding cache {cache_path}: {exc}")
            return None

        if embs.ndim != 2 or embs.shape[0] != len(all_chunks):
            print(
                "Chunk embedding cache mismatch: "
                f"{embs.shape} embeddings for {len(all_chunks)} chunks. "
                "Falling back to per-query encode."
            )
            return None

        norms = np.linalg.norm(embs, axis=1, keepdims=True)
        embs = embs / np.maximum(norms, 1e-12)
        print(f"Loaded chunk embedding cache: {cache_path} ({embs.shape[0]} chunks)")
        return {chunk.chunk_id: embs[i] for i, chunk in enumerate(all_chunks)}

    def _cached_embeddings_for(self, chunks: list[ChunkRecord]) -> np.ndarray | None:
        if self.chunk_embedding_map is None:
            return None

        embeddings = []
        for chunk in chunks:
            emb = self.chunk_embedding_map.get(chunk.chunk_id)
            if emb is None:
                return None
            embeddings.append(emb)
        return np.vstack(embeddings) if embeddings else None

    def retrieve_for_question(
        self,
        question:   str,
        public_ids: Optional[list[str]] = None,
        query_emb:  Optional[np.ndarray] = None,
        top_docs:   int = 3,
    ) -> tuple[list[RetrievedChunk], list[str]]:
        """
        Args:
            question:   câu hỏi
            public_ids: nếu có → dùng trực tiếp, bỏ qua DocIndexer search
            query_emb:  embedding của query đã encode sẵn.
                        Nếu None → tự encode 1 lần, tái sử dụng cho cả
                        DocIndexer search lẫn chunk-level dense retrieve.
            top_docs:   số docs lấy từ DocIndexer khi không có public_ids

        Returns:
            (retrieved_chunks, selected_doc_ids)
        """
        # Encode query 1 lần — dùng chung cho DocIndexer + chunk dense retrieve
        if query_emb is None:
            query_emb = self.retriever.embedder.encode(
                question, normalize_embeddings=True
            )
        else:
            query_emb = np.asarray(query_emb)
            norm = np.linalg.norm(query_emb)
            if norm > 0:
                query_emb = query_emb / norm

        if public_ids:
            selected_doc_ids = public_ids
            print(f"  [DocScope] direct → {selected_doc_ids}")
        else:
            results          = self.doc_indexer.search(question, query_emb=query_emb, top_k=top_docs)
            selected_doc_ids = [r["doc_id"] for r in results]
            print(
                f"  [DocScope] DocIndexer → {selected_doc_ids} "
                f"(rrf={[round(r['rrf_score'], 4) for r in results]})"
            )

        doc_chunks_map = {
            doc_id: self.chunk_map.get(doc_id, [])
            for doc_id in selected_doc_ids
            if self.chunk_map.get(doc_id)
        }

        if not doc_chunks_map:
            print(f"  [WARN] No chunks found for {selected_doc_ids}")
            return [], selected_doc_ids

        # Truyền query_emb xuống để retrieve_from_documents không encode lại
        all_retrieved: list[RetrievedChunk] = []
        for doc_id, chunks in doc_chunks_map.items():
            self.retriever._cached_chunk_embs = self._cached_embeddings_for(chunks)
            all_retrieved.extend(
                self.retriever._hybrid_retrieve_from_doc(chunks, question, doc_id, query_emb)
            )
        self.retriever._cached_chunk_embs = None

        if all_retrieved:
            scores = self.retriever.reranker.predict(
                [(question, c["text"]) for c in all_retrieved]
            )
            for c, s in zip(all_retrieved, scores):
                c["rerank_score"] = float(s)

        all_retrieved.sort(key=lambda x: x["rerank_score"], reverse=True)
        chunks = all_retrieved[:self.retriever.final_top_k]

        return chunks, selected_doc_ids


def create_multi_doc_retriever(
    embedding_model: str = "AITeamVN/Vietnamese_Embedding_v2",
    rerank_model:    str = "BAAI/bge-reranker-v2-m3",
) -> MultiDocRetriever:
    return MultiDocRetriever(embedding_model, rerank_model)


if __name__ == "__main__":
    print("This module is typically used as part of the full pipeline")
