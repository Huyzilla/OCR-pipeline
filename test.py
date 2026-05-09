from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import chromadb
import pandas as pd
from openai import OpenAI
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer
from tqdm import tqdm

DEFAULT_QUESTION_CSV = Path("question.csv")
DEFAULT_CHROMA_PATH = "chroma_db_viettel"
DEFAULT_COLLECTION_NAME = "rag"
DEFAULT_EMBEDDING_MODEL = "AITeamVN/Vietnamese_Embedding_v2"
DEFAULT_RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_OUTPUT_PATH = Path("task2_batch_output_check.csv")
DEFAULT_LIMIT = 991
DEFAULT_TOP_K = 50
DEFAULT_RERANK_TOP_K = 5
DEFAULT_HYBRID_BM25_WEIGHT = 0.7  # BM25: 70%, Vector: 30%
PUBLIC_DOC_PATTERN = re.compile(r"(?i)\bpublic[\s_:-]*(\d{1,4})\b")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def _load_openai_api_key() -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key.strip()

    env_path = Path(".env")
    if not env_path.exists():
        return None

    try:
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "OPENAI_API_KEY":
                cleaned = value.strip().strip('"').strip("'")
                return cleaned or None
    except Exception:
        return None

    return None


DEFAULT_API_KEY = _load_openai_api_key()


def parse_answer(answer_text: str) -> Tuple[int, str]:
    if not isinstance(answer_text, str):
        return 0, ""

    label_match = re.search(r"(?im)^\s*(?:đáp\s*án|dap\s*an)\s*:\s*(.*)$", answer_text)
    if not label_match:
        return 0, ""

    answer_section = label_match.group(1).strip().upper()

    if answer_section in {"NONE", "NO ANSWER", "KHÔNG CÓ", "KHONG CO", "KHÔNG ĐỦ THÔNG TIN", "KHONG DU THONG TIN"}:
        return 0, ""

    # Chỉ nhận format A / B / C / D / AB / A,C,D / A B C
    cleaned = re.sub(r"[^A-D]", "", answer_section)

    if not cleaned:
        return 0, ""

    ordered_unique = []
    for letter in cleaned:
        if letter not in ordered_unique:
            ordered_unique.append(letter)

    return len(ordered_unique), ",".join(ordered_unique)


def format_question(row: pd.Series) -> str:
    return (
        f"Question: {row['Question']}\n"
        f"A: {row['A']}\n"
        f"B: {row['B']}\n"
        f"C: {row['C']}\n"
        f"D: {row['D']}"
    )


def extract_target_document_id(text: str) -> str | None:
    if not isinstance(text, str):
        return None

    match = PUBLIC_DOC_PATTERN.search(text)
    if not match:
        return None

    number = int(match.group(1))
    return f"Public{number:03d}"


class BatchRAGPipeline:
    def __init__(
        self,
        chroma_path: str,
        collection_name: str,
        embedding_model_name: str,
        reranker_model_name: str,
        openai_model: str,
        openai_api_key: str,
        hybrid_bm25_weight: float,
        debug_csv_path: str | None = None,
    ) -> None:
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set.")

        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.reranker = CrossEncoder(reranker_model_name)
        self.llm_client = OpenAI(api_key=openai_api_key)
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.chroma_client.get_collection(name=collection_name)
        self.openai_model = openai_model
        self.hybrid_bm25_weight = max(0.0, min(1.0, hybrid_bm25_weight))
        self.debug_csv_path = Path(debug_csv_path) if debug_csv_path else None

        # BM25 index on full corpus
        self.all_docs: List[str] = []
        self.all_metadatas: List[Dict[str, Any]] = []
        self.bm25_index: BM25Okapi | None = None
        self._build_bm25_index()
        
        # Fusion tracking
        self.last_fusion_time: float = 0.0
        self.last_context_token_count: int = 0
        self.last_use_fusion: bool = False

    def _append_debug_csv(self, row: Dict[str, Any]) -> None:
        if not self.debug_csv_path:
            return

        self.debug_csv_path.parent.mkdir(parents=True, exist_ok=True)
        file_exists = self.debug_csv_path.exists()
        fieldnames = [
            "query",
            "query_tokens",
            "target_document_id",
            "top_bm25_results",
            "note",
        ]
        with self.debug_csv_path.open("a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({name: row.get(name, "") for name in fieldnames})

    @staticmethod
    def _tokenize_for_bm25(text: str) -> List[str]:
        text = (text or "").lower()
        # Remove punctuation, normalize whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        # Split into tokens
        tokens  = re.findall(r'\w+', text, flags=re.UNICODE)
        return tokens

    @staticmethod
    def _normalize_scores(scores: Sequence[float]) -> List[float]:
        if not scores:
            return []
        min_score = min(scores)
        max_score = max(scores)
        if max_score - min_score <= 1e-12:
            return [0.0 for _ in scores]
        return [(score - min_score) / (max_score - min_score) for score in scores]
    
    def _build_bm25_index(self) -> None:
        """Build BM25 index từ toàn bộ corpus trong Chroma"""
        print("Building BM25 index on full corpus...")
        try:
            results = self.collection.get(
                include=["documents", "metadatas"]
            )

            self.all_docs = results.get("documents", []) or []
            self.all_metadatas = results.get("metadatas", []) or []

            if not self.all_docs:
                print("No documents found in Chroma collection")
                return
            
            # tokenize toàn bộ corpus
            tokenized_docs = [
                self._tokenize_for_bm25(doc)
                for doc in self.all_docs
            ]

            # Build BM25
            self.bm25_index = BM25Okapi(tokenized_docs)
            
            print(f"BM25 index built: {len(self.all_docs)} documents")

        except Exception as e:
            print(f"Error building BM25 index: {e}")
            self.bm25_index = None

    def _find_doc_index_by_meta(self, target_meta: Dict[str, Any]) -> int | None:
        """Tìm index của doc dựa vào metadata"""
        if not isinstance(target_meta, dict):
            return None

        target_doc_id = target_meta.get("document_id")
        target_hierarchy = target_meta.get("hierarchy_path")

        for idx, meta in enumerate(self.all_metadatas):
            if meta is None:
                continue

            if (meta.get("document_id") == target_doc_id and
                meta.get("hierarchy_path") == target_hierarchy):
                return idx
            
        return None 
    
    def retrieve_hybrid(
        self, 
        query: str, 
        top_k: int, 
        target_document_id: str | None = None
    ) -> dict:
        """
        Hybrid retrieval: BM25 trên toàn bộ corpus + Vector similarity.
        Merge results và return top-k.
        """
        
        if not self.bm25_index or not self.all_docs:
            print("BM25 index not available, falling back to vector-only")
            return self._retrieve_vector_only(query, top_k, target_document_id)
        
        # STEP 1: BM25 trên TOÀN BỘ corpus
        tokenized_query = self._tokenize_for_bm25(query)
        bm25_scores = self.bm25_index.get_scores(tokenized_query).tolist()
        
        top_bm25_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:5]
        top_bm25_results = []
        for idx in top_bm25_indices:
            meta = self.all_metadatas[idx] if idx < len(self.all_metadatas) else {}
            meta = meta if isinstance(meta, dict) else {}
            top_bm25_results.append(
                {
                    "score": round(float(bm25_scores[idx]), 6),
                    "document_id": meta.get("document_id", ""),
                    "hierarchy_path": meta.get("hierarchy_path", ""),
                }
            )
        
        # Filter by target_document_id nếu có
        if target_document_id:
            for idx, meta in enumerate(self.all_metadatas):
                meta_dict = meta if isinstance(meta, dict) else {}
                if meta_dict.get("document_id") != target_document_id:
                    bm25_scores[idx] = -float('inf')
        
        # Get top indices từ BM25 (lấy 2x để có buffer)
        valid_indices = [i for i, s in enumerate(bm25_scores) if s > -float('inf')]
        if not valid_indices:
            self._append_debug_csv(
                {
                    "query": query,
                    "query_tokens": json.dumps(tokenized_query, ensure_ascii=False),
                    "target_document_id": target_document_id or "",
                    "top_bm25_results": json.dumps(top_bm25_results, ensure_ascii=False),
                    "note": "No valid BM25 indices after filtering",
                }
            )
            return {"documents": [[]], "metadatas": [[]], "indices": []}

        self._append_debug_csv(
            {
                "query": query,
                "query_tokens": json.dumps(tokenized_query, ensure_ascii=False),
                "target_document_id": target_document_id or "",
                "top_bm25_results": json.dumps(top_bm25_results, ensure_ascii=False),
                "note": "",
            }
        )
        
        bm25_top_indices = sorted(
            valid_indices, 
            key=lambda i: bm25_scores[i], 
            reverse=True
        )[:top_k * 2]
        
        # STEP 2: Vector similarity trên TOÀN BỘ corpus 
        query_emb = self.embedding_model.encode([query]).tolist()
        
        # Filter by document_id nếu có
        where_clause = None
        if target_document_id:
            where_clause = {"document_id": target_document_id}
        
        try:
            vector_results = self.collection.query(
                query_embeddings=query_emb,
                n_results=min(top_k * 2, len(self.all_docs)),
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            print(f"Vector retrieval error: {e}")
            vector_results = {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        
        vector_docs = vector_results.get("documents", [[]])[0] if vector_results else []
        vector_distances = vector_results.get("distances", [[]])[0] if vector_results else []
        vector_metadatas = vector_results.get("metadatas", [[]])[0] if vector_results else []
        
        # STEP 3: Merge BM25 + Vector 
        # Build set của merged indices
        merged_data = {}  # {index: (doc, meta, bm25_score, vector_score)}
        
        # Add BM25 results
        for idx in bm25_top_indices:
            if idx < len(self.all_docs):
                merged_data[idx] = {
                    "doc": self.all_docs[idx],
                    "meta": self.all_metadatas[idx],
                    "bm25_score": bm25_scores[idx],
                    "vector_score": 0.0
                }
        
        # Add Vector results and update vector scores
        for v_doc, v_meta, v_dist in zip(vector_docs, vector_distances, vector_metadatas):
            # Normalize metadata entries to dict to avoid attribute errors
            meta_candidate = v_meta if isinstance(v_meta, dict) else {}
            idx = self._find_doc_index_by_meta(meta_candidate)
            if idx is not None:
                vector_score = -float(v_dist)
                if idx not in merged_data:
                    merged_data[idx] = {
                        "doc": v_doc,
                        "meta": v_meta,
                        "bm25_score": bm25_scores[idx] if idx < len(bm25_scores) else 0.0,
                        "vector_score": vector_score
                    }
                else:
                    merged_data[idx]["vector_score"] = vector_score
        
        if not merged_data:
            return {"documents": [[]], "metadatas": [[]], "indices": []}
        
        # STEP 4: Compute Hybrid Scores 
        indices_list = list(merged_data.keys())
        bm25_scores_list = [merged_data[idx]["bm25_score"] for idx in indices_list]
        vector_scores_list = [merged_data[idx]["vector_score"] for idx in indices_list]
        
        norm_bm25 = self._normalize_scores(bm25_scores_list)
        norm_vector = self._normalize_scores(vector_scores_list)
        
        hybrid_scores = {}
        for i, idx in enumerate(indices_list):
            # Hybrid = BM25_weight * norm_bm25 + Vector_weight * norm_vector
            hybrid_scores[idx] = (
                self.hybrid_bm25_weight * norm_bm25[i] +
                (1.0 - self.hybrid_bm25_weight) * norm_vector[i]
            )
        
        # Top-K hybrid
        top_hybrid_indices = sorted(
            indices_list,
            key=lambda idx: hybrid_scores.get(idx, 0),
            reverse=True
        )[:top_k]
        
        # STEP 5: Build Results
        selected_docs = [self.all_docs[idx] for idx in top_hybrid_indices if idx < len(self.all_docs)]
        selected_metas = [self.all_metadatas[idx] for idx in top_hybrid_indices if idx < len(self.all_metadatas)]
        
        return {
            "documents": [selected_docs],
            "metadatas": [selected_metas],
            "indices": top_hybrid_indices
        }
 
    def _retrieve_vector_only(
        self,
        query: str,
        top_k: int,
        target_document_id: str | None = None
    ) -> dict:
        """Fallback: Vector-only retrieval"""
        query_emb = self.embedding_model.encode([query]).tolist()
        
        where_clause = None
        if target_document_id:
            where_clause = {"document_id": target_document_id}
        
        try:
            results = self.collection.query(
                query_embeddings=query_emb,
                n_results=top_k,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            return results
        except Exception as e:
            print(f"Vector retrieval error: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        
    @staticmethod
    def _build_context(results: dict, top_indices: Sequence[int]) -> Tuple[str, List[Dict[str, Any]]]:
        context_parts: List[str] = []
        context_items: List[Dict[str, Any]] = []

        for idx in top_indices:
            meta = results["metadatas"][0][idx] if idx < len(results["metadatas"][0]) else {}
            meta = meta or {}
            doc_id = meta.get("document_id", "Unknown")
            hierarchy = meta.get("hierarchy_path", "")
            chunk_type = meta.get("chunk_type", "text")
 
            if chunk_type == "table" and meta.get("raw_html"):
                content = meta["raw_html"]
            else:
                content = results["documents"][0][idx] if idx < len(results["documents"][0]) else ""
 
            source_ref = f"[Nguồn: {doc_id} | {hierarchy}]"
            context_parts.append(f"{source_ref}\n{content}")
            context_items.append(
                {
                    "document_id": doc_id,
                    "hierarchy_path": hierarchy,
                    "chunk_type": chunk_type,
                    "content": content,
                }
            )
 
        return "\n\n".join(context_parts), context_items

    # def retrieve(self, query: str, top_k: int, target_document_id: str | None = None) -> dict:
    #     query_emb = self.embedding_model.encode([query]).tolist()
    #     query_kwargs = {
    #         "query_embeddings": query_emb,
    #         "n_results": top_k,
    #         "include": ["documents", "metadatas", "distances"],
    #     }
    #     if target_document_id:
    #         query_kwargs["where"] = {"document_id": target_document_id}

    #     return self.collection.query(
    #         **query_kwargs,
    #     )

    def rerank(self, query: str, docs: Sequence[str], top_k: int) -> List[Tuple[str, float, int]]:
        if not docs:
            return []

        pairs = [(query, doc) for doc in docs]
        scores = self.reranker.predict(pairs)
        ranked = sorted(
            [(doc, float(score), idx) for idx, (doc, score) in enumerate(zip(docs, scores))],
            key=lambda item: item[1],
            reverse=True,
        )
        return ranked[:top_k]

    # def hybrid_rank_indices(self, query: str, results: dict, top_k: int) -> List[int]:
    #     docs = results.get("documents", [[]])[0] if results else []
    #     distances = results.get("distances", [[]])[0] if results else []
    #     if not docs:
    #         return []

    #     if len(distances) != len(docs):
    #         distances = [0.0 for _ in docs]

    #     tokenized_docs = [self._tokenize_for_bm25(doc) for doc in docs]
    #     tokenized_query = self._tokenize_for_bm25(query)

    #     bm25 = BM25Okapi(tokenized_docs)
    #     bm25_scores = bm25.get_scores(tokenized_query).tolist()
    #     vector_scores = [-float(distance) for distance in distances]

    #     normalized_bm25 = self._normalize_scores(bm25_scores)
    #     normalized_vector = self._normalize_scores(vector_scores)

    #     hybrid_scores = [
    #         self.hybrid_alpha * v + (1.0 - self.hybrid_alpha) * b
    #         for v, b in zip(normalized_vector, normalized_bm25)
    #     ]

    #     ranked_indices = sorted(range(len(docs)), key=lambda idx: hybrid_scores[idx], reverse=True)
    #     return ranked_indices[:top_k]

    def fuse_chunks_to_context(self, question: str, chunks: List[str]) -> str:
        """
        Fuse multiple chunks into a compact context (~600-800 tokens).
        Removes redundant info and keeps only question-relevant content.
        Falls back to simple join if LLM fails.
        """
        if not chunks:
            return ""
        
        try:
            chunks_text = "\n\n---\n\n".join(chunks)
            response = self.llm_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Bạn là chuyên gia tóm tắt và lọc thông tin.\n"
                            "Nhiệm vụ: Đọc câu hỏi và 5 đoạn văn bản, chỉ giữ lại thông tin trực tiếp liên quan đến câu hỏi.\n"
                            "- Loại bỏ thông tin trùng lặp, không cần thiết\n"
                            "- Giữ các định nghĩa, con số, ví dụ quan trọng\n"
                            "- Tổng length: ~600-800 tokens (khoảng 400-600 từ)\n"
                            "- Trả về văn bản ngắn gọn, dễ đọc"
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"[CÂU HỎI]\n{question}\n\n"
                            f"[CÁC ĐOẠN VĂNBẢN]\n{chunks_text}\n\n"
                            f"Hãy lọc và tóm tắt chỉ giữ thông tin cần thiết cho câu hỏi trên."
                        ),
                    },
                ],
                temperature=0.1,
            )
            fused = response.choices[0].message.content or ""
            return fused.strip() if fused else "\n\n".join(chunks)
        except Exception as e:
            print(f"Warning: Fusion LLM call failed ({e}), falling back to raw chunks")
            return "\n\n".join(chunks)

    def answer(self, question: str, context: str) -> str:
        response = self.llm_client.chat.completions.create(
            model=self.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Bạn là một chuyên gia phân tích dữ liệu và giải bài tập trắc nghiệm dựa trên ngữ cảnh.\n"
                        "Nhiệm vụ: Đọc kỹ ngữ cảnh, suy luận logic, rồi chọn đáp án đúng trong A, B, C, D.\n\n"

                        "Quy tắc bắt buộc:\n"
                        "1. Chỉ sử dụng thông tin có trong ngữ cảnh được cung cấp. Tuyệt đối không tự suy diễn thông tin bên ngoài.\n"

                        "2. Nếu ngữ cảnh không đủ để xác định đáp án, bắt buộc trả:\n"
                        "Giải thích: Không đủ thông tin trong ngữ cảnh để xác định đáp án.\n"
                        "Kiểm tra: Không có đủ căn cứ để đối chiếu với các phương án.\n"
                        "Đáp án: NONE\n"

                        "3. Với câu hỏi tính toán, phải trình bày bước tính từ số liệu trong ngữ cảnh.\n"

                        "4. Nếu câu hỏi có yếu tố thứ tự (ví dụ: đúng thứ tự, lần lượt, theo trình tự), "
                        "phải đối chiếu chính xác thứ tự giữa kết luận và từng phương án.\n"

                        "5. Trước khi trả đáp án cuối, bắt buộc kiểm tra lại từng phương án A, B, C, D "
                        "với kết luận đã nêu trong phần Giải thích.\n"

                        "6. Nếu phần Giải thích và phần Kiểm tra mâu thuẫn nhau, phải sửa lại đáp án theo phần Kiểm tra.\n\n"

                        "BẮT BUỘC trả về đúng cấu trúc 3 phần:\n"
                        "Giải thích: <lập luận dựa trên ngữ cảnh>\n"
                        "Kiểm tra: <đối chiếu từng đáp án A, B, C, D với kết luận>\n"
                        "Đáp án: <A/B/C/D hoặc nhiều đáp án như AB, ACD; nếu không đủ thông tin thì ghi NONE>"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "[NGỮ CẢNH]\n"
                        f"{context if context else 'Không có ngữ cảnh.'}\n\n"
                        "[CÂU HỎI]\n"
                        f"{question}\n\n"
                        "Hãy suy luận từng bước và trả lời theo đúng định dạng:\n"
                        "Giải thích: ...\n"
                        "Kiểm tra: ...\n"
                        "Đáp án: ..."
                    ),
                },
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content or ""

    def run_one(
        self,
        question_row: pd.Series,
        top_k: int,
        rerank_top_k: int,
        use_fusion: bool = False,
    ) -> Tuple[str, str, str, List[Dict[str, Any]]]:
        """
        Run QA pipeline for one question.
        
        Args:
            question_row: Question data row
            top_k: Top-K docs after hybrid retrieval
            rerank_top_k: Top-K docs after reranking
            use_fusion: If True, fuse chunks before answering
            
        Returns:
            (formatted_answer, raw_answer, llm_context, context_items)
            
        Note: fusion_time and context_token_count are stored as instance variables:
              self.last_fusion_time, self.last_context_token_count
        """
        import time
        
        question_only = str(question_row.get("Question", ""))
        question_full = format_question(question_row)
        target_document_id = extract_target_document_id(question_full)
        
        # Retrieve using Hybrid BM25 + Vectors
        results = self.retrieve_hybrid(
            question_full, 
            top_k=top_k,
            target_document_id=target_document_id
        )
 
        docs = results["documents"][0] if results and results.get("documents") else []
        fusion_start = time.time()
        self.last_fusion_time = 0.0
        self.last_use_fusion = use_fusion
        
        if not docs:
            context = ""
            context_items: List[Dict[str, Any]] = []
        else:
            # Rerank 
            reranked = self.rerank(question_only, docs, top_k=rerank_top_k)
            rerank_indices = [item[2] for item in reranked]
            
            context, context_items = self._build_context(results, rerank_indices)
            
            # Apply fusion if enabled
            if use_fusion and rerank_indices:
                reranked_docs = [docs[idx] for idx in rerank_indices]
                context = self.fuse_chunks_to_context(question_only, reranked_docs)
                self.last_fusion_time = time.time() - fusion_start
        
        # Calculate token count (approximation: words / 0.75)
        words = len(context.split())
        self.last_context_token_count = max(1, int(words / 0.75))
        
        raw_answer = self.answer(question_full, context)
        num_correct, answers = parse_answer(raw_answer)
 
        if num_correct <= 0:
            formatted = "0,"
        elif num_correct == 1:
            formatted = f"1,{answers}"
        else:
            formatted = f'{num_correct},"{answers}"'
 
        return formatted, raw_answer, context, context_items


def load_questions(path: Path, limit: int) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file câu hỏi: {path}")

    df = pd.read_csv(path)
    required_columns = {"Question", "A", "B", "C", "D"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Thiếu cột bắt buộc: {missing}")

    return df.head(limit).copy()


def write_predictions(output_path: Path, rows: List[str]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        for line in rows:
            f.write(f"{line}\n")


def write_context_log(output_path: Path, rows: List[Dict[str, Any]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def load_existing_predictions(output_path: Path) -> List[str]:
    if not output_path.exists():
        return []

    rows: List[str] = []
    with output_path.open("r", encoding="utf-8") as f:
        for line in f:
            value = line.strip()
            if value:
                rows.append(value)
    return rows


def load_existing_context_log(output_path: Path) -> List[Dict[str, Any]]:
    if not output_path.exists():
        return []

    try:
        data = json.loads(output_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch QA pipeline using ChromaDB + Hybrid BM25+Vector + Reranker + OpenAI")
    parser.add_argument("--question_csv", default=str(DEFAULT_QUESTION_CSV), help="Path to question.csv")
    parser.add_argument("--chroma_path", default=DEFAULT_CHROMA_PATH, help="Path to ChromaDB persistent store")
    parser.add_argument("--collection_name", default=DEFAULT_COLLECTION_NAME, help="Chroma collection name")
    parser.add_argument("--embedding_model", default=DEFAULT_EMBEDDING_MODEL, help="SentenceTransformer embedding model")
    parser.add_argument("--reranker_model", default=DEFAULT_RERANKER_MODEL, help="CrossEncoder reranker model")
    parser.add_argument("--openai_model", default=DEFAULT_OPENAI_MODEL, help="OpenAI chat model")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output CSV file path")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Number of first questions to run")
    parser.add_argument("--top_k", type=int, default=DEFAULT_TOP_K, help="Top-K docs after hybrid rank")
    parser.add_argument("--rerank_top_k", type=int, default=DEFAULT_RERANK_TOP_K, help="Top-K docs after CrossEncoder reranking")
    parser.add_argument(
        "--hybrid_bm25_weight",
        type=float,
        default=DEFAULT_HYBRID_BM25_WEIGHT,
        help="Weight for BM25 in hybrid scoring (0..1). Vector weight is 1-this. Default: 0.7 (70% BM25, 30% Vector)",
    )
    parser.add_argument("--api_key", default=DEFAULT_API_KEY, help="OpenAI API key")
    parser.add_argument(
        "--context_output_json",
        default=None,
        help="Optional path to save LLM context log JSON. Default: <output_stem>_contexts.json",
    )
    parser.add_argument(
        "--debug_csv",
        default=None,
        help="Optional path to save retrieval debug info as UTF-8 CSV instead of printing to console.",
    )
    parser.add_argument(
        "--use_fusion",
        action="store_true",
        help="Use context fusion (LLM filters chunks to remove redundancy and keep only relevant info)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing output file by skipping already processed questions",
    )
    args = parser.parse_args()
 
    questions_path = Path(args.question_csv)
    output_path = Path(args.output)
    context_output_path = (
        Path(args.context_output_json)
        if args.context_output_json
        else output_path.with_name(f"{output_path.stem}_contexts.json")
    )
 
    df_questions = load_questions(questions_path, limit=args.limit)
    pipeline = BatchRAGPipeline(
        chroma_path=args.chroma_path,
        collection_name=args.collection_name,
        embedding_model_name=args.embedding_model,
        reranker_model_name=args.reranker_model,
        openai_model=args.openai_model,
        openai_api_key=args.api_key,
        hybrid_bm25_weight=args.hybrid_bm25_weight,
        debug_csv_path=args.debug_csv,
    )
 
    predictions: List[str] = load_existing_predictions(output_path) if args.resume else []
    context_log: List[Dict[str, Any]] = load_existing_context_log(context_output_path) if args.resume else []
 
    already_done = len(predictions)
    if already_done > len(df_questions):
        raise ValueError(
            f"Output has {already_done} rows, but current run only has {len(df_questions)} questions (--limit)."
        )
 
    if already_done > len(context_log):
        print(
            f"Warning: context log has fewer rows ({len(context_log)}) than predictions ({already_done}). "
            "Context log will continue from current state."
        )
 
    if args.resume and already_done > 0:
        print(f"Resuming from question {already_done + 1} (already processed: {already_done})")
 
    if already_done >= len(df_questions):
        print("Nothing to process: all questions in current --limit are already completed.")
        return
 
    first_new_raw_answer = ""
    pending_questions = df_questions.iloc[already_done:]
    for q_idx, (_, row) in enumerate(
        tqdm(pending_questions.iterrows(), total=len(pending_questions), desc="Processing questions"),
        start=already_done + 1,
    ):
        formatted_answer, raw_answer, llm_context, context_items = pipeline.run_one(
            row,
            top_k=args.top_k,
            rerank_top_k=args.rerank_top_k,
            use_fusion=args.use_fusion,
        )
        predictions.append(formatted_answer)
        if not first_new_raw_answer:
            first_new_raw_answer = raw_answer
        context_log.append(
            {
                "question_index": q_idx,
                "question": str(row.get("Question", "")),
                "choices": {
                    "A": str(row.get("A", "")),
                    "B": str(row.get("B", "")),
                    "C": str(row.get("C", "")),
                    "D": str(row.get("D", "")),
                },
                "formatted_answer": formatted_answer,
                "raw_answer": raw_answer,
                "llm_context": llm_context,
                "context_items": context_items,
                "use_fusion": pipeline.last_use_fusion,
                "context_token_count": pipeline.last_context_token_count,
                "fusion_time": pipeline.last_fusion_time,
            }
        )
 
        # Checkpoint after each question
        write_predictions(output_path, predictions)
        write_context_log(context_output_path, context_log)
 
    print(f"\nOK -> {output_path}")
    print(f"Context log -> {context_output_path}")
    print(f"Processed {len(predictions)} questions")
    # if first_new_raw_answer:
    #     print(f"\nFirst raw answer:\n{first_new_raw_answer}")


if __name__ == "__main__":
    main()