"""Hybrid QA evaluation with rerank and multi-answer output."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Iterable

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize_vi(text: str) -> list[str]:
    clean = re.sub(r"[^\w\s]", " ", normalize(text))
    return [t for t in clean.split() if len(t) > 1]


def reciprocal_rank_fusion(rankings: Iterable[list[int]], k: int = 60) -> dict[int, float]:
    fused: dict[int, float] = {}
    for ranking in rankings:
        for r, idx in enumerate(ranking):
            fused[idx] = fused.get(idx, 0.0) + 1.0 / (k + r + 1)
    return fused


def top_k_indices(values: np.ndarray, k: int) -> list[int]:
    if len(values) == 0:
        return []
    k = min(k, len(values))
    if k <= 0:
        return []
    partial = np.argpartition(-values, k - 1)[:k]
    return partial[np.argsort(-values[partial])].tolist()


def load_all_chunk_texts(chunk_dir: Path) -> list[str]:
    texts: list[str] = []
    chunk_files = sorted(chunk_dir.glob("*/*_chunks.json"))
    for chunk_file in chunk_files:
        try:
            with chunk_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                txt = str(item.get("page_content", "")).strip()
                if txt:
                    texts.append(txt)
        except Exception as e:
            print(f"Warning: skip {chunk_file} ({e})")
    return texts


def parse_answer_text(text: str) -> list[str]:
    """Parse model output to list of answer labels A/B/C/D."""
    match = re.search(r"ANS\s*:\s*([^\n\r]+)", text, flags=re.IGNORECASE)
    candidate = match.group(1) if match else text
    if "?" in candidate:
        return []
    labels = re.findall(r"[ABCD]", candidate.upper())
    ordered = []
    for lbl in labels:
        if lbl not in ordered:
            ordered.append(lbl)
    return ordered


class QwenAnswerer:
    def __init__(self, model_name: str, max_new_tokens: int = 48) -> None:
        self.enabled = False
        self.max_new_tokens = max_new_tokens
        self.model_name = model_name
        self.tokenizer = None
        self.model = None

        print(f"Loading LLM: {model_name} ...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype="auto",
                device_map="auto",
            )
            self.enabled = True
        except Exception as e:
            print(f"Warning: cannot load LLM {model_name}. Fallback to non-LLM scoring. Error: {e}")

    def answer(self, question: str, options: dict[str, str], contexts: list[str]) -> list[str]:
        if not self.enabled or self.model is None or self.tokenizer is None:
            return []

        context_block = "\n\n".join([f"[CTX-{i+1}] {c}" for i, c in enumerate(contexts[:6])])
        options_block = "\n".join([f"{k}. {v}" for k, v in options.items() if v])

        system_prompt = (
            "Ban la tro ly trac nghiem. "
            "Chi duoc dung thong tin trong CONTEXT de chon dap an. "
            "Dap an co the gom 1 hoac nhieu lua chon. "
            "Neu khong du can cu, tra ve ANS: ?. "
            "Chi tra ve duy nhat 1 dong theo dinh dang: ANS: A hoac ANS: A,B hoac ANS: ?."
        )
        user_prompt = (
            f"CONTEXT:\n{context_block}\n\n"
            f"QUESTION: {question}\n"
            f"OPTIONS:\n{options_block}\n\n"
            "Hay tra loi dung format yeu cau."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        output_ids = self.model.generate(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            do_sample=False,
            temperature=None,
            top_p=None,
            eos_token_id=self.tokenizer.eos_token_id,
        )
        generated_ids = output_ids[0][inputs["input_ids"].shape[1] :]
        text = self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
        return parse_answer_text(text)


class HybridQAPipeline:
    def __init__(
        self,
        chunk_texts: list[str],
        embedding_model: str,
        rerank_model: str,
        bm25_top_k: int = 60,
        dense_top_k: int = 60,
        fused_top_k: int = 20,
        rerank_top_k: int = 8,
    ) -> None:
        self.chunk_texts = chunk_texts
        self.bm25_top_k = bm25_top_k
        self.dense_top_k = dense_top_k
        self.fused_top_k = fused_top_k
        self.rerank_top_k = rerank_top_k

        print("Loading embedding model...")
        self.embedder = SentenceTransformer(embedding_model)
        print("Loading reranker model...")
        self.reranker = None
        self.use_cross_encoder = False
        try:
            self.reranker = CrossEncoder(rerank_model)
            self.use_cross_encoder = True
        except Exception as e:
            # Fallback to semantic rerank to keep pipeline runnable.
            print(f"Warning: cannot load CrossEncoder ({e}). Use semantic rerank fallback.")

        print("Building BM25 corpus...")
        tokenized = [tokenize_vi(t) for t in self.chunk_texts]
        self.bm25 = BM25Okapi(tokenized)

        print("Encoding chunks for dense retrieval...")
        emb = self.embedder.encode(
            self.chunk_texts,
            batch_size=64,
            show_progress_bar=True,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        self.chunk_embeddings = emb.astype(np.float32)

    def retrieve(self, question: str) -> list[int]:
        # Sparse BM25
        q_tokens = tokenize_vi(question)
        sparse_scores = np.array(self.bm25.get_scores(q_tokens), dtype=np.float32)
        bm25_rank = top_k_indices(sparse_scores, self.bm25_top_k)

        # Dense cosine (dot for normalized vectors)
        q_emb = self.embedder.encode(
            [question],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )[0].astype(np.float32)
        dense_scores = self.chunk_embeddings @ q_emb
        dense_rank = top_k_indices(dense_scores, self.dense_top_k)

        # Hybrid fusion
        fused = reciprocal_rank_fusion([bm25_rank, dense_rank])
        fused_rank = sorted(fused, key=lambda idx: fused[idx], reverse=True)[: self.fused_top_k]

        # Rerank final candidates
        if not fused_rank:
            return []

        if self.use_cross_encoder and self.reranker is not None:
            pairs = [(question, self.chunk_texts[idx]) for idx in fused_rank]
            rerank_scores = self.reranker.predict(pairs)
            ranked = sorted(
                zip(fused_rank, rerank_scores),
                key=lambda x: float(x[1]),
                reverse=True,
            )
        else:
            q_emb = self.embedder.encode(
                [question],
                normalize_embeddings=True,
                convert_to_numpy=True,
            )[0].astype(np.float32)
            sem_scores = [float(self.chunk_embeddings[idx] @ q_emb) for idx in fused_rank]
            ranked = sorted(
                zip(fused_rank, sem_scores),
                key=lambda x: x[1],
                reverse=True,
            )
        return [idx for idx, _ in ranked[: self.rerank_top_k]]

    def choose_answers(self, question: str, options: dict[str, str], top_chunk_ids: list[int]) -> list[str]:
        if not top_chunk_ids:
            return []

        contexts = [self.chunk_texts[i] for i in top_chunk_ids]
        ctx_embeddings = self.embedder.encode(
            contexts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype(np.float32)

        option_keys = [k for k in ["A", "B", "C", "D"] if options.get(k, "").strip()]
        option_texts = [f"Cau hoi: {question}\nLua chon: {options[k]}" for k in option_keys]
        opt_embeddings = self.embedder.encode(
            option_texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype(np.float32)

        scores: dict[str, float] = {}
        context_joined = normalize(" ".join(contexts))

        for key, opt_emb in zip(option_keys, opt_embeddings):
            semantic = float(np.max(ctx_embeddings @ opt_emb))
            tokens = [t for t in tokenize_vi(options[key]) if len(t) >= 3][:8]
            lexical_hits = sum(1 for t in tokens if t in context_joined)
            lexical = lexical_hits / max(1, len(tokens))
            scores[key] = 0.8 * semantic + 0.2 * lexical

        if not scores:
            return []

        best = max(scores.values())
        selected = [k for k, v in scores.items() if v >= best - 0.04 and v >= 0.30]
        return sorted(selected)


def run_qa_evaluation(
    question_csv: Path,
    chunk_dir: Path,
    output_file: Path,
    max_questions: int,
    embedding_model: str,
    rerank_model: str,
    llm_model: str,
    use_llm: bool,
    llm_max_new_tokens: int,
) -> None:
    print("Loading chunks...")
    chunk_texts = load_all_chunk_texts(chunk_dir)
    if not chunk_texts:
        raise RuntimeError("No chunks found in chunk directory")

    print(f"Loaded {len(chunk_texts)} chunks")
    qa = HybridQAPipeline(
        chunk_texts=chunk_texts,
        embedding_model=embedding_model,
        rerank_model=rerank_model,
    )
    llm_answerer = QwenAnswerer(llm_model, max_new_tokens=llm_max_new_tokens) if use_llm else None

    results: list[str] = []
    with question_csv.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            if max_questions > 0 and idx > max_questions:
                break

            question = row.get("Question", "").strip()
            if not question:
                continue

            options = {
                "A": row.get("A", "").strip(),
                "B": row.get("B", "").strip(),
                "C": row.get("C", "").strip(),
                "D": row.get("D", "").strip(),
            }

            print(f"[{idx}] {question[:80]}...")
            top_chunk_ids = qa.retrieve(question)

            answers: list[str] = []
            if llm_answerer is not None and llm_answerer.enabled:
                contexts = [chunk_texts[i] for i in top_chunk_ids]
                answers = llm_answerer.answer(question, options, contexts)

            if not answers:
                answers = qa.choose_answers(question, options, top_chunk_ids)

            num_corrects = len(answers)
            if answers:
                answer_text = ",".join(answers)
                if len(answers) > 1:
                    answer_text = f'"{answer_text}"'
            else:
                answer_text = "?"
            results.append(f"{num_corrects},{answer_text}")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        for line in results:
            f.write(line + "\n")

    print(f"Saved {len(results)} lines to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hybrid QA evaluation with rerank and optional Qwen LLM")
    parser.add_argument("--question_csv", default="question.csv")
    parser.add_argument("--chunk_dir", default="chunk_outputs_final")
    parser.add_argument("--output", default="result.md")
    parser.add_argument("--max_questions", type=int, default=100, help="0 means full file")
    parser.add_argument(
        "--embedding_model",
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    )
    parser.add_argument(
        "--rerank_model",
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
    )
    parser.add_argument(
        "--llm_model",
        default="Qwen/Qwen2.5-3B-Instruct",
    )
    parser.add_argument(
        "--disable_llm",
        action="store_true",
        help="Disable LLM answer generation and use retrieval scoring only",
    )
    parser.add_argument("--llm_max_new_tokens", type=int, default=48)

    args = parser.parse_args()
    run_qa_evaluation(
        question_csv=Path(args.question_csv),
        chunk_dir=Path(args.chunk_dir),
        output_file=Path(args.output),
        max_questions=args.max_questions,
        embedding_model=args.embedding_model,
        rerank_model=args.rerank_model,
        llm_model=args.llm_model,
        use_llm=not args.disable_llm,
        llm_max_new_tokens=args.llm_max_new_tokens,
    )
