"""Drop-in thay thế sentence_transformers.CrossEncoder bằng ONNX Runtime (INT8).

Chỉ cần API .predict(pairs) — đúng thứ baseline_fusion.retrieval.rerank() dùng.

Cách dùng trong prepare_retrieval():

    from baseline_fusion.onnx_reranker import OnnxCrossEncoder
    reranker = OnnxCrossEncoder(args.rerank_model, num_threads=8)
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer


class OnnxCrossEncoder:
    """Tương thích API .predict() của sentence_transformers.CrossEncoder."""

    def __init__(
        self,
        model_dir: str | Path,
        num_threads: int = 8,
        max_length: int = 512,
        batch_size: int = 32,
        apply_sigmoid: bool = True,
    ):
        model_dir = Path(model_dir)
        if not model_dir.exists():
            raise FileNotFoundError(f"Không thấy thư mục model: {model_dir}")

        onnx_files = sorted(model_dir.glob("*.onnx"))
        if not onnx_files:
            raise FileNotFoundError(f"Không thấy file .onnx trong {model_dir}")

        so = ort.SessionOptions()
        so.intra_op_num_threads = num_threads
        so.inter_op_num_threads = 1
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        self.session = ort.InferenceSession(
            str(onnx_files[0]), so, providers=["CPUExecutionProvider"]
        )
        self.input_names = {i.name for i in self.session.get_inputs()}

        # PHẢI dùng fast tokenizer: vocab đã prune nên chỉ có tokenizer.json
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_dir))

        self.max_length = max_length
        self.batch_size = batch_size
        self.apply_sigmoid = apply_sigmoid

        n_params_mb = onnx_files[0].stat().st_size / 1024**2
        print(f"  ONNX reranker: {onnx_files[0].name} ({n_params_mb:.1f} MB, "
              f"{num_threads} threads)")

    def predict(
        self,
        sentence_pairs,
        batch_size: int | None = None,
        show_progress_bar: bool = False,
        **_kwargs,
    ) -> np.ndarray:
        """sentence_pairs: list[(query, doc)] -> np.ndarray điểm số."""
        if not sentence_pairs:
            return np.asarray([], dtype=np.float32)

        bs = batch_size or self.batch_size
        scores: list[float] = []

        for i in range(0, len(sentence_pairs), bs):
            batch = sentence_pairs[i : i + bs]
            queries = [p[0] for p in batch]
            docs = [p[1] for p in batch]

            enc = self.tokenizer(
                queries,
                docs,
                padding=True,
                truncation=True,
                max_length=self.max_length,
                return_tensors="np",
            )

            feed = {
                "input_ids": enc["input_ids"].astype(np.int64),
                "attention_mask": enc["attention_mask"].astype(np.int64),
            }
            # XLM-R không dùng token_type_ids; chỉ truyền nếu model có input đó
            if "token_type_ids" in self.input_names and "token_type_ids" in enc:
                feed["token_type_ids"] = enc["token_type_ids"].astype(np.int64)

            logits = self.session.run(None, feed)[0]
            logits = logits.squeeze(-1) if logits.ndim == 2 else logits
            scores.extend(np.atleast_1d(logits).tolist())

        out = np.asarray(scores, dtype=np.float32)

        # CrossEncoder mặc định áp sigmoid khi num_labels == 1.
        # Sigmoid đơn điệu tăng -> KHÔNG đổi thứ hạng, chỉ để rerank_score
        # trong debug log giữ nguyên thang [0, 1] như trước.
        if self.apply_sigmoid:
            out = 1.0 / (1.0 + np.exp(-out))

        return out