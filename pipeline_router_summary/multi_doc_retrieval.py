#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-document retrieval: Hybrid retrieval trong top-2 documents với BGE rerank
"""

from pathlib import Path
from typing import Optional, TypedDict
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer

try:
    from qa.utils import ChunkRecord
except ImportError:
    # Fallback for when running as submodule
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from qa.utils import ChunkRecord


class RetrievedChunk(TypedDict):
    """Kiểu dữ liệu cho retrieved chunk"""
    chunk_id: str
    text: str
    doc_id: str
    score: float
    rerank_score: float


class MultiDocRetriever:
    """
    Hybrid retrieval trong top-2 documents:
    - Retrieve 5 chunks mỗi document
    - Merge và rerank 10 chunks
    - Lấy top 5 cuối cùng
    """
    
    def __init__(
        self,
        embedding_model: str = "AITeamVN/Vietnamese_Embedding_v2",
        rerank_model: str = "BAAI/bge-reranker-v2-m3",
        chunks_per_doc: int = 5,
        final_top_k: int = 5
    ):
        """
        Initialize multi-document retriever
        
        Args:
            embedding_model: Dense embedding model
            rerank_model: BGE rerank model
            chunks_per_doc: Số chunks lấy từ mỗi document
            final_top_k: Số chunks cuối cùng sau rerank
        """
        print("Loading embedding model...")
        self.embedder = SentenceTransformer(embedding_model)
        
        print("Loading rerank model...")
        self.reranker = CrossEncoder(rerank_model)
        
        self.chunks_per_doc = chunks_per_doc
        self.final_top_k = final_top_k
        self.bm25_top_k = chunks_per_doc + 2  # Lấy thêm để có chọn lựa
        self.dense_top_k = chunks_per_doc + 2
    
    def _hybrid_retrieve_from_doc(
        self,
        chunks: list[ChunkRecord],
        query: str,
        doc_id: str
    ) -> list[RetrievedChunk]:
        """
        Hybrid retrieve từ một document
        
        Args:
            chunks: List of chunks từ document này
            query: Query text
            doc_id: Document ID
            
        Returns:
            List of RetrievedChunk sorted by hybrid score
        """
        if not chunks:
            return []
        
        chunk_texts = [c.text for c in chunks]
        chunk_id_to_chunk = {c.chunk_id: c for c in chunks}
        
        # BM25 retrieval
        bm25 = BM25Okapi([self._tokenize(t) for t in chunk_texts])
        query_tokens = self._tokenize(query)
        bm25_scores = bm25.get_scores(query_tokens)
        bm25_top_indices = np.argsort(bm25_scores)[-self.bm25_top_k:][::-1]
        
        # Dense retrieval
        query_embedding = self.embedder.encode(query)
        chunk_embeddings = self.embedder.encode(chunk_texts)
        dense_scores = np.dot(chunk_embeddings, query_embedding)
        dense_top_indices = np.argsort(dense_scores)[-self.dense_top_k:][::-1]
        
        # Reciprocal rank fusion
        combined_scores = {}
        for rank, idx in enumerate(bm25_top_indices):
            combined_scores[idx] = combined_scores.get(idx, 0) + 1 / (rank + 60)
        for rank, idx in enumerate(dense_top_indices):
            combined_scores[idx] = combined_scores.get(idx, 0) + 1 / (rank + 60)
        
        # Lấy top chunks_per_doc
        top_indices = sorted(combined_scores.keys(), key=lambda x: combined_scores[x], reverse=True)[:self.chunks_per_doc]
        
        retrieved = []
        for idx in top_indices:
            chunk = chunks[idx]
            retrieved.append({
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "doc_id": doc_id,
                "score": combined_scores[idx],
                "rerank_score": 0.0
            })
        
        return retrieved
    
    def retrieve_from_documents(
        self,
        query: str,
        doc_chunks_map: dict[str, list[ChunkRecord]]
    ) -> list[RetrievedChunk]:
        """
        Retrieve chunks từ multiple documents
        
        Args:
            query: Query text
            doc_chunks_map: {doc_id: [chunks]}
            
        Returns:
            List of RetrievedChunk (top-k) sorted by rerank score
        """
        all_retrieved = []
        
        # Retrieve từ mỗi document
        for doc_id, chunks in doc_chunks_map.items():
            doc_chunks = self._hybrid_retrieve_from_doc(chunks, query, doc_id)
            all_retrieved.extend(doc_chunks)
        
        # Rerank tất cả chunks
        # CrossEncoder cần thứ tự: (query, passage)
        if all_retrieved:
            contexts = [(query, c["text"]) for c in all_retrieved]
            rerank_scores = self.reranker.predict(contexts)
            
            for i, chunk in enumerate(all_retrieved):
                chunk["rerank_score"] = float(rerank_scores[i])
        
        # Sort by rerank score và lấy top_k
        all_retrieved.sort(key=lambda x: x["rerank_score"], reverse=True)
        return all_retrieved[:self.final_top_k]
    
    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenization cho BM25"""
        return text.lower().split()


class MultiDocPipeline:
    """
    Full pipeline: Router → Summary search → Multi-doc retrieve
    """
    
    def __init__(
        self,
        summary_indexer,  # SummaryIndexer instance
        all_chunks: list[ChunkRecord],
        embedding_model: str = "AITeamVN/Vietnamese_Embedding_v2",
        rerank_model: str = "BAAI/bge-reranker-v2-m3"
    ):
        """
        Initialize pipeline
        
        Args:
            summary_indexer: SummaryIndexer instance
            all_chunks: List of all chunks
            embedding_model: Dense embedding model
            rerank_model: BGE rerank model
        """
        self.summary_indexer = summary_indexer
        self.retriever = MultiDocRetriever(embedding_model, rerank_model)
        
        # Build chunk map: doc_id -> chunks
        self.chunk_map = {}
        for chunk in all_chunks:
            # Extract doc_id từ chunk_id (format: Public001::chunk::0)
            parts = chunk.chunk_id.split("::")
            doc_id = parts[0] if len(parts) > 1 else chunk.chunk_id
            if doc_id not in self.chunk_map:
                self.chunk_map[doc_id] = []
            self.chunk_map[doc_id].append(chunk)
    
    def retrieve_for_question(
        self,
        question: str,
        public_ids: Optional[list[str]] = None,
        use_summary_search: bool = True
    ) -> tuple[list[RetrievedChunk], list[str]]:
        """
        Retrieve chunks cho một question
        
        Args:
            question: Câu hỏi
            public_ids: List of public_id từ router (nếu có)
            use_summary_search: Có dùng summary search không?
            
        Returns:
            (retrieved_chunks, selected_doc_ids)
        """
        # Decide target documents
        if public_ids and use_summary_search:
            # Có public_id trong câu hỏi
            selected_doc_ids = public_ids
            print(f"Using public IDs from question: {selected_doc_ids}")
        else:
            # Không có, dùng summary search để tìm top-2 documents
            summary_results = self.summary_indexer.search_summaries(question, top_k=2)
            selected_doc_ids = [r["doc_id"] for r in summary_results]
            print(f"Selected documents from summary search: {selected_doc_ids}")
        
        # Build doc_chunks_map chỉ cho selected documents
        doc_chunks_map = {
            doc_id: self.chunk_map.get(doc_id, [])
            for doc_id in selected_doc_ids
        }
        
        # Loại bỏ documents không có chunks
        doc_chunks_map = {k: v for k, v in doc_chunks_map.items() if v}
        
        if not doc_chunks_map:
            print(f"Warning: No chunks found for documents {selected_doc_ids}")
            return [], selected_doc_ids
        
        # Multi-doc retrieve + rerank
        retrieved_chunks = self.retriever.retrieve_from_documents(question, doc_chunks_map)
        
        return retrieved_chunks, selected_doc_ids


def create_multi_doc_retriever(
    embedding_model: str = "AITeamVN/Vietnamese_Embedding_v2",
    rerank_model: str = "BAAI/bge-reranker-v2-m3"
) -> MultiDocRetriever:
    """Factory function"""
    return MultiDocRetriever(embedding_model, rerank_model)


if __name__ == "__main__":
    # Test multi-doc retriever
    print("This module is typically used as part of the full pipeline")
