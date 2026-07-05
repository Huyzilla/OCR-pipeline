from __future__ import annotations

from dataclasses import dataclass

from .paths import PROJECT_ROOT


DEFAULT_ANSWER_MODEL = "gpt-4o-mini"


@dataclass(frozen=True)
class ModelOption:
    label: str
    model_id: str
    kind: str = ""
    truncate_dim: int | None = None


@dataclass(frozen=True)
class RetrievalSettings:
    embedding_label: str
    embedding_model: str
    embedding_truncate_dim: int | None
    reranker_label: str
    reranker_model: str
    router_label: str
    router_kind: str
    router_model: str
    dense_top_k: int = 10
    bm25_top_k: int = 10
    final_top_k: int = 5
    answer_model: str = DEFAULT_ANSWER_MODEL
    answer_max_tokens: int = 900


EMBEDDING_OPTIONS = {
    "BM25-only nhanh": ModelOption(
        label="BM25-only nhanh",
        model_id="none",
    ),
    "Vietnamese_embedding_v2": ModelOption(
        label="Vietnamese_embedding_v2",
        model_id="AITeamVN/Vietnamese_Embedding_v2",
    ),
    "Embedding fine-tune": ModelOption(
        label="Embedding fine-tune",
        model_id=str(PROJECT_ROOT / "models" / "embed_gist_mnr"),
        truncate_dim=512,
    ),
}

RERANKER_OPTIONS = {
    "Không rerank": ModelOption(
        label="Không rerank",
        model_id="none",
    ),
    "BGE reranker v2 m3": ModelOption(
        label="BGE reranker v2 m3",
        model_id="BAAI/bge-reranker-v2-m3",
    ),
    "MiniLM H384 pruned fine-tune": ModelOption(
        label="MiniLM H384 pruned fine-tune",
        model_id=str(PROJECT_ROOT / "models" / "MiniLM_H384_pruned_ft"),
    ),
}

ROUTER_OPTIONS = {
    "Mặc định tra cứu": ModelOption(
        label="Mặc định tra cứu",
        model_id="none",
        kind="none",
    ),
    "GPT-4o mini": ModelOption(
        label="GPT-4o mini",
        model_id="gpt-4o-mini",
        kind="gpt",
    ),
    "SBERT routing": ModelOption(
        label="SBERT routing",
        model_id=str(PROJECT_ROOT / "models" / "sbert_routing"),
        kind="sbert",
    ),
}
