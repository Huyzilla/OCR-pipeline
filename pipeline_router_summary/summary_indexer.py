#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Summary Indexer: Store summaries in JSON + ChromaDB
"""

import json
import chromadb
from pathlib import Path
from typing import Optional
from sentence_transformers import SentenceTransformer
from .summary_generator import DocumentSummary


class SummaryIndexer:
    """
    Index summaries trong JSON (backup) + ChromaDB (runtime search)
    """
    
    def __init__(
        self,
        embedding_model: str = "AITeamVN/Vietnamese_Embedding_v2",
        chroma_db_path: Optional[Path] = None,
        json_output_path: Optional[Path] = None
    ):
        """
        Initialize summary indexer
        
        Args:
            embedding_model: Embedding model để embed summaries
            chroma_db_path: Path tới ChromaDB directory
            json_output_path: Path tới file JSON để lưu summaries
        """
        print(f"Loading embedding model: {embedding_model}")
        self.embedder = SentenceTransformer(embedding_model)
        
        self.chroma_db_path = chroma_db_path or Path("chroma_db_summaries")
        self.json_output_path = json_output_path or Path("summaries.json")
        
        # Initialize ChromaDB
        print(f"Initializing ChromaDB at {self.chroma_db_path}")
        self.client = chromadb.PersistentClient(path=str(self.chroma_db_path))
        self.collection = self.client.get_or_create_collection(
            name="summaries",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.embeddings_cache = {}
        self.summaries_data = []
    
    def add_summaries(self, summaries: list[DocumentSummary]) -> None:
        """
        Add summaries vào index
        
        Args:
            summaries: List of DocumentSummary
        """
        print(f"Indexing {len(summaries)} summaries...")
        
        # Embed summaries
        summary_texts = [s["summary_text"] for s in summaries]
        embeddings = self.embedder.encode(summary_texts, show_progress_bar=True)
        
        # Prepare data cho ChromaDB
        doc_ids = [s["doc_id"] for s in summaries]
        metadatas = [
            {
                "chunk_count": str(s["chunk_count"]),
                "token_count": str(s["token_count"])
            }
            for s in summaries
        ]
        
        # Upsert vào ChromaDB (an toàn khi chạy lại nhiều lần, tránh lỗi duplicate ID)
        self.collection.upsert(
            ids=doc_ids,
            embeddings=embeddings.tolist(),
            documents=summary_texts,
            metadatas=metadatas
        )
        
        # Lưu JSON backup
        self.summaries_data = summaries
        self._save_json()
        
        print(f"✓ Added {len(summaries)} summaries to index")
    
    def _save_json(self) -> None:
        """Save summaries to JSON file"""
        self.json_output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.json_output_path, 'w', encoding='utf-8') as f:
            json.dump(self.summaries_data, f, ensure_ascii=False, indent=2)
        print(f"✓ Saved summaries to {self.json_output_path}")
    
    def load_json(self) -> list[DocumentSummary]:
        """Load summaries từ JSON file"""
        if not self.json_output_path.exists():
            print(f"JSON file not found: {self.json_output_path}")
            return []
        
        with open(self.json_output_path, 'r', encoding='utf-8') as f:
            self.summaries_data = json.load(f)
        
        print(f"✓ Loaded {len(self.summaries_data)} summaries from {self.json_output_path}")
        return self.summaries_data
    
    def search_summaries(self, query: str, top_k: int = 2) -> list[dict]:
        """
        Tìm kiếm top-k documents dựa vào summary
        
        Args:
            query: Query text (câu hỏi)
            top_k: Số documents cần trả về
            
        Returns:
            List of {doc_id, summary_text, distance, chunk_count}
        """
        # Embed query
        query_embedding = self.embedder.encode(query)
        
        # Search trong ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "distances", "metadatas"]
        )
        
        # Format results
        output = []
        for i in range(len(results['ids'][0])):
            output.append({
                "doc_id": results['ids'][0][i],
                "summary_text": results['documents'][0][i],
                "distance": results['distances'][0][i],
                "chunk_count": int(results['metadatas'][0][i]['chunk_count']),
                "token_count": int(results['metadatas'][0][i]['token_count'])
            })
        
        return output
    
    def reset_index(self) -> None:
        """Reset ChromaDB collection"""
        try:
            self.client.delete_collection(name="summaries")
            self.collection = self.client.get_or_create_collection(
                name="summaries",
                metadata={"hnsw:space": "cosine"}
            )
            print("✓ ChromaDB index reset")
        except Exception as e:
            print(f"Error resetting index: {e}")
    
    def get_stats(self) -> dict:
        """Get index statistics"""
        count = self.collection.count()
        return {
            "total_summaries": count,
            "json_file": str(self.json_output_path),
            "chroma_db_path": str(self.chroma_db_path),
            "summaries_loaded": len(self.summaries_data)
        }


def create_summary_indexer(
    embedding_model: str = "AITeamVN/Vietnamese_Embedding_v2",
    chroma_db_path: Optional[Path] = None,
    json_output_path: Optional[Path] = None
) -> SummaryIndexer:
    """Factory function để tạo summary indexer"""
    return SummaryIndexer(embedding_model, chroma_db_path, json_output_path)


if __name__ == "__main__":
    # Test summary indexer
    indexer = SummaryIndexer()
    
    # Test data
    test_summaries = [
        {
            "doc_id": "Public001",
            "summary_text": "Chính sách lương và phúc lợi: Lương trả hàng tháng, phúc lợi bao gồm bảo hiểm y tế, hỗ trợ ăn trưa. 15 ngày phép/năm.",
            "chunk_count": 3,
            "token_count": 45
        },
        {
            "doc_id": "Public002",
            "summary_text": "Quy trình tuyển dụng: CV → Phỏng vấn HR → Phỏng vấn chuyên môn → Offer letter → Onboarding",
            "chunk_count": 4,
            "token_count": 35
        }
    ]
    
    # Add summaries
    indexer.add_summaries(test_summaries)
    
    # Search
    print("\nSearching summaries:")
    results = indexer.search_summaries("Chính sách lương phúc lợi", top_k=1)
    for r in results:
        print(f"Doc: {r['doc_id']}, Distance: {r['distance']:.3f}")
        print(f"Summary: {r['summary_text']}\n")
    
    # Stats
    print("Index stats:", indexer.get_stats())
