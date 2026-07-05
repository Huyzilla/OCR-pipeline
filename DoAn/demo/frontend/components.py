from __future__ import annotations

import pandas as pd
import streamlit as st

from bootstrap import setup

setup()

from backend.models import (
    DEFAULT_ANSWER_MODEL,
    EMBEDDING_OPTIONS,
    RERANKER_OPTIONS,
    ROUTER_OPTIONS,
    RetrievalSettings,
)
from backend.worker_client import warmup_models_in_worker


def render_model_settings(prefix: str) -> RetrievalSettings:
    st.sidebar.header("Model")
    embedding_key = st.sidebar.selectbox(
        "Embedding",
        list(EMBEDDING_OPTIONS.keys()),
        key=f"{prefix}_embedding",
    )
    reranker_key = st.sidebar.selectbox(
        "Reranker",
        list(RERANKER_OPTIONS.keys()),
        index=0,
        key=f"{prefix}_reranker",
    )
    router_key = st.sidebar.selectbox(
        "Routing",
        list(ROUTER_OPTIONS.keys()),
        key=f"{prefix}_router",
    )

    with st.sidebar.expander("Tùy chỉnh truy hồi"):
        dense_top_k = st.slider("Dense top-k", 1, 50, 10, key=f"{prefix}_dense_top_k")
        bm25_top_k = st.slider("BM25 top-k", 1, 50, 10, key=f"{prefix}_bm25_top_k")
        final_top_k = st.slider("Số nguồn đưa vào LLM", 1, 12, 5, key=f"{prefix}_final_top_k")
        answer_model = st.text_input("LLM trả lời", DEFAULT_ANSWER_MODEL, key=f"{prefix}_answer_model")
        answer_max_tokens = st.slider(
            "Max tokens",
            200,
            2000,
            900,
            step=100,
            key=f"{prefix}_answer_max_tokens",
        )

    embedding = EMBEDDING_OPTIONS[embedding_key]
    reranker = RERANKER_OPTIONS[reranker_key]
    router = ROUTER_OPTIONS[router_key]

    return RetrievalSettings(
        embedding_label=embedding.label,
        embedding_model=embedding.model_id,
        embedding_truncate_dim=embedding.truncate_dim,
        reranker_label=reranker.label,
        reranker_model=reranker.model_id,
        router_label=router.label,
        router_kind=router.kind,
        router_model=router.model_id,
        dense_top_k=dense_top_k,
        bm25_top_k=bm25_top_k,
        final_top_k=final_top_k,
        answer_model=answer_model,
        answer_max_tokens=answer_max_tokens,
    )


def render_model_warmup(
    prefix: str,
    settings: RetrievalSettings,
    *,
    chunk_dir,
    doc_scopes: tuple[str, ...] = (),
) -> bool:
    state_key = f"{prefix}_warmup_result"
    ready_key = f"{prefix}_warmup_ready"

    cols = st.columns([1, 3])
    with cols[0]:
        clicked = st.button("Load model trước", key=f"{prefix}_warmup_button")
    with cols[1]:
        st.caption(
            "Nên bấm trước khi hỏi nếu chọn embedding/reranker/router dùng model. "
            "Nếu dùng BM25-only thì bước này rất nhanh."
        )

    if clicked:
        with st.spinner("Đang load/kiểm tra model trong worker..."):
            try:
                result = warmup_models_in_worker(
                    settings,
                    chunk_dir=chunk_dir,
                    doc_scopes=doc_scopes,
                    timeout_s=900,
                )
            except Exception as exc:
                st.session_state[ready_key] = False
                st.session_state[state_key] = {"error": str(exc)}
                st.error(str(exc))
            else:
                st.session_state[ready_key] = True
                st.session_state[state_key] = result
                st.success(f"Model sẵn sàng sau {result['total_seconds']}s")

    result = st.session_state.get(state_key)
    if result:
        with st.expander("Trạng thái load model", expanded=not st.session_state.get(ready_key, False)):
            st.json(result)

    return bool(st.session_state.get(ready_key, False))


def render_answer_result(result: dict) -> None:
    st.subheader("Câu trả lời")
    st.markdown(result["answer"] or "_Không có câu trả lời._")

    for warning in result.get("warnings", []):
        st.warning(warning)

    timing = result["timing"]
    with st.expander("Chi tiết xử lý", expanded=False):
        cols = st.columns(5)
        cols[0].metric("Intent", result["intent"])
        cols[1].metric("Router", f"{timing['route_s']:.2f}s")
        cols[2].metric("Retrieve", f"{timing['retrieve_s']:.2f}s")
        cols[3].metric("Rerank", f"{timing['rerank_s']:.2f}s")
        cols[4].metric("Tổng", f"{timing['total_s']:.2f}s")
        st.caption(f"Retrieval mode: {result.get('retrieval_mode', 'unknown')}")
        st.json(result["models"])

        worker = result.get("worker")
        if worker:
            st.caption(f"Worker Python: {worker.get('python', '')}")
            if worker.get("log"):
                with st.expander("Worker log", expanded=False):
                    st.code(worker["log"][-6000:])
            if worker.get("stderr"):
                with st.expander("Worker stderr", expanded=False):
                    st.code(worker["stderr"][-6000:])

    with st.expander("Nguồn tham khảo", expanded=True):
        rows = []
        for i, chunk in enumerate(result["chunks"], start=1):
            rows.append(
                {
                    "#": i,
                    "Tài liệu": chunk.get("doc"),
                    "BM25": chunk.get("bm25_rank"),
                    "Dense": chunk.get("dense_rank"),
                    "Rerank": round(chunk.get("rerank_score", 0.0), 4),
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        for i, chunk in enumerate(result["chunks"], start=1):
            with st.expander(f"Nguồn {i}: {chunk.get('doc')}", expanded=i == 1):
                if chunk.get("section_hint"):
                    st.caption(chunk["section_hint"])
                st.write(chunk.get("text", ""))
