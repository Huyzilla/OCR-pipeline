from __future__ import annotations

import sys
from pathlib import Path

FRONTEND_DIR = Path(__file__).resolve().parents[1]
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

import streamlit as st

from bootstrap import setup

setup()

from backend.paths import CORPUS_CHUNK_DIR
from backend.service import get_corpus_summary
from backend.worker_client import ask_question_in_worker
from components import render_answer_result, render_model_settings, render_model_warmup


st.set_page_config(page_title="Corpus QA", layout="wide")

st.title("Hỏi trong kho corpus")
st.write("Dùng khi bạn không biết câu trả lời nằm trong tài liệu nào.")

settings = render_model_settings("corpus")
summary = get_corpus_summary()

cols = st.columns(2)
cols[0].metric("Tài liệu có sẵn", summary["document_count"])
cols[1].metric("Kho chunk", "Sẵn sàng" if summary["chunk_ready"] else "Chưa sẵn sàng")

render_model_warmup(
    "corpus",
    settings,
    chunk_dir=CORPUS_CHUNK_DIR,
    doc_scopes=(),
)

question = st.text_area(
    "Câu hỏi",
    height=130,
    placeholder="Nhập câu hỏi cần tra cứu trong kho tài liệu...",
)

if st.button("Hỏi corpus", type="primary", disabled=not summary["chunk_ready"]):
    with st.spinner("Đang chạy worker RAG và sinh câu trả lời..."):
        try:
            result = ask_question_in_worker(
                question,
                settings,
                chunk_dir=CORPUS_CHUNK_DIR,
                doc_scopes=(),
            )
        except Exception as exc:
            st.error(str(exc))
        else:
            render_answer_result(result)
