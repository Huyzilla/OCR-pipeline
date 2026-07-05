"""
Offline pre-process: Build doc_vector cho mỗi Public_ID
Chiến lược:
  - text_chunks >= 3  → TextRank weighted mean embedding
  - text_chunks 1-2   → blend(mean_text, mean_table) 70/30
  - text_chunks = 0   → hierarchy_weighted_mean (depth + position score)

Output:
  - doc_vectors.pkl   : {doc_id: np.ndarray(dim,)}
  - bm25_index.pkl    : {doc_id: {"tokens": [...], "text": "..."}}  → dùng lúc query
"""

import json
import pickle
import re
from pathlib import Path
from typing import Optional

import numpy as np
from rank_bm25 import BM25Okapi


# TextRank 

def textrank_weights(embeddings: np.ndarray, damping: float = 0.85, max_iter: int = 100) -> np.ndarray:
    """
    Tính trọng số TextRank cho từng chunk dựa trên similarity graph.

    Args:
        embeddings: shape (n, dim), đã normalize
        damping:    hệ số damping của PageRank
        max_iter:   số vòng lặp tối đa

    Returns:
        weights: shape (n,), tổng = 1
    """
    n = len(embeddings)
    if n == 1:
        return np.array([1.0])

    # Ma trận similarity
    sim = embeddings @ embeddings.T   # (n, n)
    np.fill_diagonal(sim, 0.0)

    # Normalize theo hàng 
    row_sums = sim.sum(axis=1, keepdims=True)
    row_sums = np.where(row_sums == 0, 1, row_sums)
    sim /= row_sums

    # Power iteration
    scores = np.ones(n) / n
    for _ in range(max_iter):
        new_scores = (1 - damping) / n + damping * sim.T @ scores
        if np.abs(new_scores - scores).max() < 1e-6:
            break
        scores = new_scores

    # Normalize thành weights
    scores = np.clip(scores, 0, None)
    total  = scores.sum()
    return scores / total if total > 0 else np.ones(n) / n


# Hierarchy score

def hierarchy_depth_score(hierarchy_path: str) -> float:
    """
    Tính depth score từ hierarchy_path dạng "A > B > C".
    Depth càng sâu → score càng cao (chunk chi tiết hơn).
    """
    if not hierarchy_path or not hierarchy_path.strip():
        return 1.0
    depth = len([p for p in hierarchy_path.split(">") if p.strip()])
    return float(depth)


def hierarchy_weighted_mean(
    chunks: list[dict],
    embeddings: np.ndarray,
) -> np.ndarray:
    """
    Weighted mean embedding cho doc toàn bảng.
    Weight = depth_score * position_score (chunks đầu quan trọng hơn).

    Args:
        chunks:     list chunk dict (có metadata.hierarchy_path, chunk_index)
        embeddings: shape (n, dim)

    Returns:
        doc_vector: shape (dim,), normalized
    """
    n = len(chunks)
    weights = np.zeros(n)

    for i, chunk in enumerate(chunks):
        meta       = chunk.get("metadata", {})
        depth      = hierarchy_depth_score(meta.get("hierarchy_path", ""))
        # Position score: chunks đầu tiên quan trọng hơn (giảm dần)
        chunk_idx  = meta.get("chunk_index", i)
        total_chunks = max(n, 1)
        position   = 1.0 - (chunk_idx / total_chunks) * 0.5   # range [0.5, 1.0]
        weights[i] = depth * position

    total = weights.sum()
    weights = weights / total if total > 0 else np.ones(n) / n

    vec = (embeddings * weights[:, None]).sum(axis=0)
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


# Doc vector builder 

def build_doc_vector(
    doc_id:          str,
    chunks:          list[dict],
    chunk_embs:      np.ndarray,   # shape (n_chunks_of_doc, dim)
) -> np.ndarray:
    """
    Build 1 doc_vector theo chiến lược phân nhánh.

    Args:
        doc_id:     "Public001"
        chunks:     list chunk dict của doc này (đã lọc theo doc_id)
        chunk_embs: embeddings tương ứng, shape (n, dim)

    Returns:
        doc_vector: shape (dim,), normalized
    """
    text_mask  = np.array([c["metadata"].get("chunk_type") == "text"  for c in chunks])
    table_mask = np.array([c["metadata"].get("chunk_type") == "table" for c in chunks])

    n_text  = int(text_mask.sum())
    n_table = int(table_mask.sum())

    text_embs  = chunk_embs[text_mask]   if n_text  > 0 else np.empty((0, chunk_embs.shape[1]))
    table_embs = chunk_embs[table_mask]  if n_table > 0 else np.empty((0, chunk_embs.shape[1]))
    text_chunks  = [c for c, m in zip(chunks, text_mask)  if m]
    table_chunks = [c for c, m in zip(chunks, table_mask) if m]

    # Nhánh 1: >= 3 text chunks + > 0 table chunks → TextRank 
    if n_text >= 3:
        weights    = textrank_weights(text_embs)
        vec_text   = (text_embs * weights[:, None]).sum(axis=0)
        if n_table > 0:
            vec_table = table_embs.mean(axis=0)
            vec = 0.85 * vec_text + 0.15 * vec_table
        else:
            vec=vec_text
        strategy   = "textrank"

    # Nhánh 2: 1-2 text chunks → blend 70/30
    elif n_text >= 1:
        mean_text  = text_embs.mean(axis=0)
        if n_table > 0:
            mean_table = table_embs.mean(axis=0)
            vec        = 0.7 * mean_text + 0.3 * mean_table
        else:
            vec        = mean_text
        strategy   = f"blend_{n_text}text_{n_table}table"

    # Nhánh 3: 0 text chunks → hierarchy weighted mean trên toàn bảng
    else:
        vec        = hierarchy_weighted_mean(table_chunks, table_embs)
        strategy   = "hierarchy_weighted"

    # Normalize
    norm = np.linalg.norm(vec)
    vec  = vec / norm if norm > 0 else vec

    print(f"  [{doc_id}] {strategy} | text={n_text} table={n_table} total={len(chunks)}")
    return vec


# BM25 tokenizer

def tokenize_vi(text: str) -> list[str]:
    clean = re.sub(r"[^\w\s]", " ", text.lower())
    return [t for t in clean.split() if len(t) > 1]


# Main builder 

def build_offline_index(
    chunk_dir:       Path,
    chunk_emb_cache: Path,
    output_dir:      Path,
) -> tuple[dict[str, np.ndarray], dict]:
    """
    Build toàn bộ offline index cho tất cả Public_IDs.

    Args:
        chunk_dir:       Path tới folder chứa các JSON chunk (rglob *.json)
        chunk_emb_cache: Path tới cache/cache_chunk_embeddings.pkl
        output_dir:      Folder lưu output

    Returns:
        doc_vectors: {doc_id: np.ndarray(dim,)}
        bm25_data:   {doc_id: {"tokens": [...], "text": "..."}}
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load chunks 
    print("Loading chunks...")
    all_chunks:    list[dict] = []
    all_chunk_ids: list[str]  = []

    for jf in sorted(chunk_dir.rglob("*.json")):
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                continue
            doc_scope = jf.parent.name   # "Public001"
            for i, item in enumerate(data):
                text = str(item.get("page_content", "")).strip()
                if not text:
                    continue
                chunk_id = item.get("metadata", {}).get("chunk_id", f"chunk::{i}")
                item["_doc_scope"] = doc_scope
                item["_chunk_id"]  = f"{doc_scope}::{chunk_id}"
                all_chunks.append(item)
                all_chunk_ids.append(item["_chunk_id"])
        except Exception as e:
            print(f"  [WARN] skip {jf}: {e}")

    print(f"Loaded {len(all_chunks)} chunks")

    # 2. Load embeddings 
    print(f"Loading embeddings from {chunk_emb_cache}...")
    with open(chunk_emb_cache, "rb") as f:
        all_embs: np.ndarray = pickle.load(f)

    assert all_embs.shape[0] == len(all_chunks), (
        f"Embedding count mismatch: {all_embs.shape[0]} embs vs {len(all_chunks)} chunks. "
        f"Rebuild cache/cache_chunk_embeddings.pkl với cùng thứ tự load."
    )
    print(f"Embeddings shape: {all_embs.shape}")

    # 3. Group theo doc 
    doc_chunk_map:  dict[str, list[dict]]       = {}
    doc_emb_map:    dict[str, list[np.ndarray]] = {}

    for i, chunk in enumerate(all_chunks):
        doc_id = chunk["_doc_scope"]
        doc_chunk_map.setdefault(doc_id, []).append(chunk)
        doc_emb_map.setdefault(doc_id, []).append(all_embs[i])

    print(f"Found {len(doc_chunk_map)} documents: {sorted(doc_chunk_map.keys())[:5]}...")

    # 4. Build doc vectors + BM25 data 
    print("\nBuilding doc vectors...")
    doc_vectors: dict[str, np.ndarray] = {}
    bm25_data:   dict[str, dict]       = {}

    for doc_id in sorted(doc_chunk_map.keys()):
        chunks     = doc_chunk_map[doc_id]
        embs       = np.array(doc_emb_map[doc_id])   # (n, dim)

        # Doc vector
        doc_vectors[doc_id] = build_doc_vector(doc_id, chunks, embs)

        # BM25: ghép toàn bộ page_content của doc
        full_text = " ".join(c.get("page_content", "") for c in chunks)
        tokens    = tokenize_vi(full_text)
        bm25_data[doc_id] = {
            "tokens": tokens,
            "text":   full_text[:500],   # preview để debug
        }

    # 5. Save
    vec_path  = output_dir / "doc_vectors.pkl"
    bm25_path = output_dir / "bm25_index.pkl"

    with open(vec_path, "wb") as f:
        pickle.dump(doc_vectors, f)
    print(f"\n✓ Saved doc_vectors → {vec_path}  ({len(doc_vectors)} docs)")

    with open(bm25_path, "wb") as f:
        pickle.dump(bm25_data, f)
    print(f"✓ Saved bm25_data   → {bm25_path}")

    # Stats
    n_text_only  = sum(
        1 for doc_id, chunks in doc_chunk_map.items()
        if all(c["metadata"].get("chunk_type") == "text" for c in chunks)
    )
    n_table_only = sum(
        1 for doc_id, chunks in doc_chunk_map.items()
        if all(c["metadata"].get("chunk_type") == "table" for c in chunks)
    )
    print(f"\nStats:")
    print(f"  Total docs:  {len(doc_vectors)}")
    print(f"  Text-only:   {n_text_only}")
    print(f"  Table-only:  {n_table_only}")
    print(f"  Mixed:       {len(doc_vectors) - n_text_only - n_table_only}")

    return doc_vectors, bm25_data


# DocIndexer (dùng lúc query)

class DocIndexer:
    """
    Load offline index và search top-k docs cho query bằng BM25 + embedding + RRF.
    """

    def __init__(self, index_dir: Path):
        """
        Args:
            index_dir: folder chứa doc_vectors.pkl và bm25_index.pkl
        """
        vec_path  = index_dir / "doc_vectors.pkl"
        bm25_path = index_dir / "bm25_index.pkl"

        assert vec_path.exists(),  f"doc_vectors.pkl not found in {index_dir}"
        assert bm25_path.exists(), f"bm25_index.pkl not found in {index_dir}"

        with open(vec_path, "rb") as f:
            self._doc_vectors: dict[str, np.ndarray] = pickle.load(f)

        with open(bm25_path, "rb") as f:
            self._bm25_data: dict[str, dict] = pickle.load(f)

        # Build BM25
        self._doc_names  = sorted(self._doc_vectors.keys())
        self._doc_matrix = np.array([self._doc_vectors[d] for d in self._doc_names])  # (n_docs, dim)

        corpus  = [self._bm25_data[d]["tokens"] for d in self._doc_names]
        self._bm25 = BM25Okapi(corpus)

        print(f"DocIndexer loaded: {len(self._doc_names)} docs")

    def search(
        self,
        query:     str,
        query_emb: Optional[np.ndarray] = None,
        top_k:     int = 2,
        k_rrf:     int = 60,
    ) -> list[dict]:
        """
        Args:
            query:     câu hỏi
            query_emb: embedding đã encode sẵn (tái sử dụng, tránh encode lại)
            top_k:     số docs trả về
            k_rrf:     hằng số RRF

        Returns:
            list[{"doc_id", "bm25_rank", "dense_rank", "rrf_score"}]
        """
        # BM25
        bm25_scores  = self._bm25.get_scores(tokenize_vi(query))
        bm25_ranking = np.argsort(bm25_scores)[::-1]

        # Dense
        if query_emb is None:
            raise ValueError("query_emb is required — encode query trước khi gọi search()")
        # Normalize nếu chưa
        norm = np.linalg.norm(query_emb)
        if norm > 0:
            query_emb = query_emb / norm
        dense_scores  = self._doc_matrix @ query_emb
        dense_ranking = np.argsort(dense_scores)[::-1]

        # RRF
        rrf:        dict[int, float] = {}
        bm25_rank:  dict[int, int]   = {}
        dense_rank: dict[int, int]   = {}

        for rank, idx in enumerate(bm25_ranking):
            rrf[idx]       = rrf.get(idx, 0.0) + 1.0 / (k_rrf + rank + 1)
            bm25_rank[idx] = rank + 1
        for rank, idx in enumerate(dense_ranking):
            rrf[idx]        = rrf.get(idx, 0.0) + 1.0 / (k_rrf + rank + 1)
            dense_rank[idx] = rank + 1

        sorted_idx = sorted(rrf, key=lambda x: rrf[x], reverse=True)[:top_k]

        return [
            {
                "doc_id":     self._doc_names[i],
                "bm25_rank":  bm25_rank[i],
                "dense_rank": dense_rank[i],
                "rrf_score":  round(rrf[i], 6),
            }
            for i in sorted_idx
        ]

    def get_stats(self) -> dict:
        return {
            "total_docs":    len(self._doc_names),
            "embedding_dim": self._doc_matrix.shape[1],
            "doc_names":     self._doc_names[:5],
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build offline doc index")
    parser.add_argument("--chunk-dir",   type=Path, default=Path("chunk_outputs_finals"))
    parser.add_argument("--emb-cache",   type=Path, default=Path("cache/cache_chunk_embeddings.pkl"))
    parser.add_argument("--output-dir",  type=Path, default=Path("doc_index"))
    args = parser.parse_args()

    doc_vectors, bm25_data = build_offline_index(
        chunk_dir       = args.chunk_dir,
        chunk_emb_cache = args.emb_cache,
        output_dir      = args.output_dir,
    )

    print("\nDone. Test search:")
    indexer = DocIndexer(args.output_dir)
    print(indexer.get_stats())
