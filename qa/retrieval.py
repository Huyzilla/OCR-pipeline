from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer

from .utils import ChunkRecord, reciprocal_rank_fusion, sanitize_for_filename, stable_texts_fingerprint, tokenize_vi, top_k_indices


class HybridQAPipeline:
    _embedder_cache: dict[str, SentenceTransformer] = {}
    _reranker_cache: dict[str, CrossEncoder | None] = {}

    def __init__(
        self,
        chunks: list[ChunkRecord],
        embedding_model: str,
        rerank_model: str,
        cache_dir: Path | None = None,
        use_cache: bool = True,
        neighbor_hops: int = 1,
        max_expanded_chunks: int = 12,
        bm25_top_k: int = 60,
        dense_top_k: int = 60,
        fused_top_k: int = 20,
        rerank_top_k: int = 8,
    ) -> None:
        self.chunks = chunks
        self.chunk_texts = [c.text for c in chunks]
        self.chunk_id_to_index = {c.chunk_id: i for i, c in enumerate(chunks)}
        self.neighbor_hops = max(0, int(neighbor_hops))
        self.max_expanded_chunks = max(1, int(max_expanded_chunks))
        self.bm25_top_k = bm25_top_k
        self.dense_top_k = dense_top_k
        self.fused_top_k = fused_top_k
        self.rerank_top_k = rerank_top_k
        self.child_candidate_k = 40
        self.min_parent_groups = 3
        self.max_parent_groups = 5
        self.cache_dir = cache_dir
        self.use_cache = use_cache
        self.child_indices = [i for i, c in enumerate(chunks) if "::child::" in c.chunk_id]
        self.has_parent_child = len(self.child_indices) > 0

        self.embedder = self._embedder_cache.get(embedding_model)
        if self.embedder is None:
            print("Loading embedding model...")
            self.embedder = SentenceTransformer(embedding_model)
            self._embedder_cache[embedding_model] = self.embedder

        self.reranker = self._reranker_cache.get(rerank_model)
        self.use_cross_encoder = self.reranker is not None
        if rerank_model not in self._reranker_cache:
            print("Loading reranker model...")
            try:
                self.reranker = CrossEncoder(rerank_model)
                self._reranker_cache[rerank_model] = self.reranker
                self.use_cross_encoder = True
            except Exception as e:
                print(f"Warning: cannot load CrossEncoder ({e}). Use semantic rerank fallback.")
                self._reranker_cache[rerank_model] = None
                self.reranker = None
                self.use_cross_encoder = False

        fingerprint = stable_texts_fingerprint(self.chunk_texts)
        safe_model = sanitize_for_filename(embedding_model)
        bm25_loaded = False
        emb_loaded = False

        bm25_cache_path: Path | None = None
        emb_cache_path: Path | None = None
        if self.use_cache and self.cache_dir is not None:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            bm25_cache_path = self.cache_dir / f"bm25_{fingerprint[:16]}.pkl"
            emb_cache_path = self.cache_dir / f"dense_{safe_model}_{fingerprint[:16]}.npy"

        if bm25_cache_path is not None and bm25_cache_path.exists():
            try:
                with bm25_cache_path.open("rb") as f:
                    self.bm25 = pickle.load(f)
                bm25_loaded = True
                print(f"Loaded BM25 cache: {bm25_cache_path}")
            except Exception as e:
                print(f"Warning: BM25 cache load failed ({e}). Rebuilding BM25...")

        if not bm25_loaded:
            print("Building BM25 corpus...")
            tokenized = [tokenize_vi(t) for t in self.chunk_texts]
            self.bm25 = BM25Okapi(tokenized)
            if bm25_cache_path is not None:
                try:
                    with bm25_cache_path.open("wb") as f:
                        pickle.dump(self.bm25, f)
                except Exception as e:
                    print(f"Warning: BM25 cache save failed ({e})")

        if emb_cache_path is not None and emb_cache_path.exists():
            try:
                self.chunk_embeddings = np.load(emb_cache_path).astype(np.float32)
                if len(self.chunk_embeddings) == len(self.chunk_texts):
                    emb_loaded = True
                    print(f"Loaded dense cache: {emb_cache_path}")
                else:
                    print("Warning: Dense cache size mismatch. Re-encoding...")
            except Exception as e:
                print(f"Warning: Dense cache load failed ({e}). Re-encoding...")

        if not emb_loaded:
            print("Encoding chunks for dense retrieval...")
            emb = self.embedder.encode(
                self.chunk_texts,
                batch_size=64,
                show_progress_bar=True,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
            self.chunk_embeddings = emb.astype(np.float32)
            if emb_cache_path is not None:
                try:
                    np.save(emb_cache_path, self.chunk_embeddings)
                except Exception as e:
                    print(f"Warning: Dense cache save failed ({e})")

    def _expand_with_neighbors(self, seed_indices: list[int]) -> list[int]:
        expanded: list[int] = []
        seen: set[int] = set()

        for seed_idx in seed_indices:
            if seed_idx not in seen:
                seen.add(seed_idx)
                expanded.append(seed_idx)

            if self.neighbor_hops <= 0:
                continue

            frontier = [seed_idx]
            local_seen = {seed_idx}
            for _ in range(self.neighbor_hops):
                next_frontier: list[int] = []
                for current_idx in frontier:
                    current_chunk = self.chunks[current_idx]
                    for neighbor_id in [current_chunk.prev_chunk_id, current_chunk.next_chunk_id]:
                        if not neighbor_id:
                            continue
                        neighbor_idx = self.chunk_id_to_index.get(neighbor_id)
                        if neighbor_idx is None or neighbor_idx in local_seen:
                            continue
                        local_seen.add(neighbor_idx)
                        next_frontier.append(neighbor_idx)
                frontier = next_frontier
                for neighbor_idx in next_frontier:
                    if neighbor_idx not in seen:
                        seen.add(neighbor_idx)
                        expanded.append(neighbor_idx)

        return expanded[: self.max_expanded_chunks]

    def _prefer_child_chunks(self, indices: list[int]) -> list[int]:
        # Parent-child chunking produces near-duplicate parent/child pairs.
        # If a child is present for a family, keep the child and drop the parent
        # so fallback scoring does not count the same evidence twice.
        child_parent_ids: set[str] = set()
        for idx in indices:
            chunk = self.chunks[idx]
            if "::child::" in chunk.chunk_id and chunk.parent_id:
                child_parent_ids.add(chunk.parent_id)

        if not child_parent_ids:
            return indices

        filtered: list[int] = []
        for idx in indices:
            chunk = self.chunks[idx]
            if chunk.chunk_id in child_parent_ids and "::child::" not in chunk.chunk_id:
                continue
            filtered.append(idx)
        return filtered

    def _top_k_from_subset(self, scores: np.ndarray, indices: list[int], k: int) -> list[int]:
        if not indices or k <= 0:
            return []
        k = min(k, len(indices))
        return sorted(indices, key=lambda idx: float(scores[idx]), reverse=True)[:k]

    def _rerank_candidates(
        self,
        question: str,
        candidate_indices: list[int],
        dense_scores: np.ndarray,
        q_emb: np.ndarray,
    ) -> list[tuple[int, float]]:
        if not candidate_indices:
            return []

        if self.use_cross_encoder and self.reranker is not None:
            pairs = [(question, self.chunk_texts[idx]) for idx in candidate_indices]
            rerank_scores = self.reranker.predict(pairs)
            ranked = sorted(zip(candidate_indices, rerank_scores), key=lambda x: float(x[1]), reverse=True)
            return [(idx, float(score)) for idx, score in ranked]

        sem_scores = [float(self.chunk_embeddings[idx] @ q_emb) for idx in candidate_indices]
        ranked = sorted(zip(candidate_indices, sem_scores), key=lambda x: x[1], reverse=True)
        return [(idx, float(score)) for idx, score in ranked]

    def _expand_child_with_siblings(self, child_idx: int) -> list[int]:
        chunk = self.chunks[child_idx]
        parent_id = chunk.parent_id
        selected: list[int] = [child_idx]

        for neighbor_id in [chunk.prev_chunk_id, chunk.next_chunk_id]:
            if not neighbor_id:
                continue
            neighbor_idx = self.chunk_id_to_index.get(neighbor_id)
            if neighbor_idx is None:
                continue
            neighbor = self.chunks[neighbor_idx]
            if "::child::" not in neighbor.chunk_id:
                continue
            if parent_id is None or neighbor.parent_id != parent_id:
                continue
            selected.append(neighbor_idx)

        return selected

    def _expand_parent_child_context(self, ranked_children: list[tuple[int, float]]) -> tuple[list[int], list[int]]:
        if not ranked_children:
            return [], []

        parent_best_score: dict[str, float] = {}
        parent_best_child: dict[str, int] = {}
        for idx, score in ranked_children:
            chunk = self.chunks[idx]
            parent_key = chunk.parent_id or chunk.chunk_id
            if parent_key not in parent_best_score or score > parent_best_score[parent_key]:
                parent_best_score[parent_key] = float(score)
                parent_best_child[parent_key] = idx

        ranked_parents = sorted(parent_best_score.items(), key=lambda x: x[1], reverse=True)
        if not ranked_parents:
            return [], []

        available = len(ranked_parents)
        target_parent_count = min(self.max_parent_groups, max(self.min_parent_groups, available))
        target_parent_count = min(target_parent_count, available)
        selected_parents = [parent_key for parent_key, _ in ranked_parents[:target_parent_count]]

        seed_indices: list[int] = []
        expanded_indices: list[int] = []
        seen: set[int] = set()

        for parent_key in selected_parents:
            child_idx = parent_best_child[parent_key]
            if child_idx not in seed_indices:
                seed_indices.append(child_idx)

            local_indices = self._expand_child_with_siblings(child_idx)
            for idx in local_indices:
                if idx in seen:
                    continue
                seen.add(idx)
                expanded_indices.append(idx)

        if len(seed_indices) > self.rerank_top_k:
            seed_indices = seed_indices[: self.rerank_top_k]

        return seed_indices, expanded_indices[: self.max_expanded_chunks]

    def _focus_seed_doc_scope(self, ranked_indices: list[int]) -> list[int]:
        # For global retrieval, fused/reranked candidates can drift across unrelated docs.
        # Keep the dominant doc scope when it is clearly supported by top-ranked seeds.
        if not ranked_indices:
            return ranked_indices

        scope_weights: dict[str, float] = {}
        for r, idx in enumerate(ranked_indices):
            scope = self.chunks[idx].doc_scope
            scope_weights[scope] = scope_weights.get(scope, 0.0) + 1.0 / (r + 1)

        if len(scope_weights) <= 1:
            return ranked_indices

        ordered = sorted(scope_weights.items(), key=lambda x: x[1], reverse=True)
        best_scope, best_weight = ordered[0]
        second_weight = ordered[1][1]
        total_weight = sum(scope_weights.values())

        # Apply scope focus only when one scope is clearly dominant.
        if total_weight <= 0:
            return ranked_indices
        dominance = best_weight / total_weight
        if dominance < 0.58 or best_weight < second_weight * 1.20:
            return ranked_indices

        filtered = [idx for idx in ranked_indices if self.chunks[idx].doc_scope == best_scope]
        if len(filtered) >= 2:
            return filtered
        return ranked_indices

    def retrieve_with_scored_details(self, question: str) -> tuple[list[int], list[int], list[dict[str, float | int | str | None]]]:
        q_tokens = tokenize_vi(question)
        sparse_scores = np.array(self.bm25.get_scores(q_tokens), dtype=np.float32)
        q_emb = self.embedder.encode([question], normalize_embeddings=True, convert_to_numpy=True)[0].astype(np.float32)
        dense_scores = self.chunk_embeddings @ q_emb
        if self.has_parent_child:
            bm25_rank = self._top_k_from_subset(sparse_scores, self.child_indices, self.child_candidate_k)
            dense_rank = self._top_k_from_subset(dense_scores, self.child_indices, self.child_candidate_k)
            fused = reciprocal_rank_fusion([bm25_rank, dense_rank])
            fused_rank = sorted(fused, key=lambda idx: fused[idx], reverse=True)[: self.child_candidate_k]
            ranked = self._rerank_candidates(question, fused_rank, dense_scores, q_emb)

            ranked_indices = [idx for idx, _ in ranked]
            ranked_indices = self._focus_seed_doc_scope(ranked_indices)
            allowed = set(ranked_indices)
            ranked = [(idx, score) for idx, score in ranked if idx in allowed]
            seed_indices, expanded_indices = self._expand_parent_child_context(ranked)
        else:
            bm25_rank = top_k_indices(sparse_scores, self.bm25_top_k)
            dense_rank = top_k_indices(dense_scores, self.dense_top_k)
            fused = reciprocal_rank_fusion([bm25_rank, dense_rank])
            fused_rank = sorted(fused, key=lambda idx: fused[idx], reverse=True)[: self.fused_top_k]
            ranked = self._rerank_candidates(question, fused_rank, dense_scores, q_emb)

            seed_indices = [idx for idx, _ in ranked[: self.rerank_top_k]]
            seed_indices = self._focus_seed_doc_scope(seed_indices)
            seed_indices = self._prefer_child_chunks(seed_indices)
            expanded_indices = self._expand_with_neighbors(seed_indices)
            expanded_indices = self._prefer_child_chunks(expanded_indices)
            expanded_indices = expanded_indices[: self.max_expanded_chunks]

        bm25_rank_map = {idx: rank + 1 for rank, idx in enumerate(bm25_rank)}
        dense_rank_map = {idx: rank + 1 for rank, idx in enumerate(dense_rank)}
        fused_rank_map = {idx: rank + 1 for rank, idx in enumerate(fused_rank)}
        rerank_score_map = {idx: float(score) for idx, score in ranked}
        seed_rank_map = {idx: rank + 1 for rank, idx in enumerate(seed_indices)}

        scored_chunks: list[dict[str, float | int | str | None]] = []
        for order, idx in enumerate(expanded_indices, start=1):
            chunk = self.chunks[idx]
            scored_chunks.append(
                {
                    "expanded_order": order,
                    "chunk_index": idx,
                    "chunk_id": chunk.chunk_id,
                    "doc_scope": chunk.doc_scope,
                    "is_seed": idx in seed_rank_map,
                    "seed_rank": seed_rank_map.get(idx),
                    "bm25_rank": bm25_rank_map.get(idx),
                    "bm25_score": float(sparse_scores[idx]) if idx in bm25_rank_map else None,
                    "dense_rank": dense_rank_map.get(idx),
                    "dense_score": float(dense_scores[idx]) if idx in dense_rank_map else None,
                    "fused_rank": fused_rank_map.get(idx),
                    "fused_score": float(fused.get(idx)) if idx in fused else None,
                    "rerank_score": rerank_score_map.get(idx),
                }
            )

        return seed_indices, expanded_indices, scored_chunks

    def retrieve_with_details(self, question: str) -> tuple[list[int], list[int]]:
        seed_indices, expanded_indices, _ = self.retrieve_with_scored_details(question)
        return seed_indices, expanded_indices

    def retrieve(self, question: str) -> list[int]:
        _, expanded_indices = self.retrieve_with_details(question)
        return expanded_indices

    def choose_answers(self, question: str, options: dict[str, str], top_chunk_ids: list[int]) -> list[str]:
        if not top_chunk_ids:
            return []

        contexts = [self.chunk_texts[i] for i in top_chunk_ids]
        ctx_embeddings = self.embedder.encode(contexts, normalize_embeddings=True, convert_to_numpy=True).astype(np.float32)

        option_keys = [k for k in ["A", "B", "C", "D"] if options.get(k, "").strip()]
        option_texts = [f"Câu hỏi: {question}\nLựa chọn: {options[k]}" for k in option_keys]
        opt_embeddings = self.embedder.encode(option_texts, normalize_embeddings=True, convert_to_numpy=True).astype(np.float32)

        scores: dict[str, float] = {}
        context_tokens = set(tokenize_vi(" ".join(contexts)))

        for key, opt_emb in zip(option_keys, opt_embeddings):
            semantic = float(np.max(ctx_embeddings @ opt_emb))
            tokens = [t for t in tokenize_vi(options[key]) if len(t) >= 3][:8]
            lexical_hits = sum(1 for t in tokens if t in context_tokens)
            lexical = lexical_hits / max(1, len(tokens))
            scores[key] = 0.8 * semantic + 0.2 * lexical

        if not scores:
            return []

        ranked_opts = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best = ranked_opts[0][1]

        # Avoid over-selecting many options when evidence is diffuse.
        selected = [k for k, v in ranked_opts if v >= best - 0.02 and v >= 0.34]
        if not selected:
            return []

        if len(selected) > 2:
            selected = [ranked_opts[0][0]]
        return sorted(selected)
