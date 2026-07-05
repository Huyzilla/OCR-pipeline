from __future__ import annotations

import sys
from pathlib import Path

FRONTEND_DIR = Path(__file__).resolve().parents[1]
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

import streamlit as st

from bootstrap import setup

setup()

from backend.service import prepare_user_document
from backend.worker_client import ask_question_in_worker
from components import render_answer_result, render_model_settings, render_model_warmup


st.set_page_config(page_title="Upload Document QA", layout="wide")

st.title("Upload tài liệu rồi hỏi")
st.write("Hệ thống chỉ mở phần hỏi sau khi tài liệu đã có OCR và chunk.")

settings = render_model_settings("upload")

uploaded_file = st.file_uploader("Tải lên PDF", type=["pdf"])
table_format = st.radio("Bảng trong OCR", ["html", "markdown"], horizontal=True)

if "active_doc" not in st.session_state:
    st.session_state.active_doc = None

if uploaded_file and st.button("Chuẩn bị tài liệu", type="primary"):
    with st.spinner("Đang kiểm tra OCR sẵn hoặc chạy OCR nếu cần..."):
        try:
            st.session_state.active_doc = prepare_user_document(
                uploaded_file.name,
                uploaded_file.getvalue(),
                table_format=table_format,
            )
        except Exception as exc:
            st.session_state.active_doc = None
            st.error(str(exc))

doc_info = st.session_state.active_doc
if not doc_info:
    st.info("Upload PDF và bấm chuẩn bị tài liệu để bắt đầu.")
    st.stop()

source_text = "Đã có OCR sẵn" if doc_info["source"] == "existing" else "OCR từ upload mới"
st.success(f"{source_text}: {doc_info['doc_id']}")

with st.expander("Xem nội dung OCR", expanded=False):
    md_path = Path(doc_info["md_path"])
    st.markdown(md_path.read_text(encoding="utf-8", errors="ignore")[:12000])

render_model_warmup(
    "upload",
    settings,
    chunk_dir=Path(doc_info["chunk_dir"]),
    doc_scopes=(str(doc_info["doc_id"]),),
)

question = st.text_area(
    "Câu hỏi cho tài liệu này",
    height=130,
    placeholder="Nhập câu hỏi cần hỏi trên tài liệu vừa chuẩn bị...",
)

if st.button("Hỏi tài liệu", type="primary"):
    with st.spinner("Đang chạy worker RAG và sinh câu trả lời..."):
        try:
            result = ask_question_in_worker(
                question,
                settings,
                chunk_dir=Path(doc_info["chunk_dir"]),
                doc_scopes=(str(doc_info["doc_id"]),),
            )
        except Exception as exc:
            st.error(str(exc))
        else:
            render_answer_result(result)
