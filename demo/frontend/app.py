from __future__ import annotations

import streamlit as st

from bootstrap import setup

setup()

from backend.preflight import get_runtime_report
from backend.service import clear_demo_cache, get_corpus_summary


st.set_page_config(page_title="RAG PDF Demo", layout="wide")

st.title("RAG PDF Demo")
st.write("Hỏi đáp tự do trên kho PDF đã OCR hoặc trên tài liệu PDF do người dùng upload.")

summary = get_corpus_summary()
cols = st.columns(3)
cols[0].metric("Tài liệu có sẵn", summary["document_count"])
cols[1].metric("Kho chunk", "Sẵn sàng" if summary["chunk_ready"] else "Chưa sẵn sàng")
cols[2].metric("Chế độ", "Corpus / Upload")

st.divider()

st.subheader("Chọn luồng ở sidebar")
st.markdown(
    """
- **Corpus QA**: hỏi trên toàn bộ kho tài liệu đã OCR sẵn.
- **Upload Document QA**: upload PDF, hệ thống kiểm tra OCR sẵn; nếu chưa có thì OCR và chunk trước khi hỏi.
"""
)

left, right = st.columns(2)
with left:
    if st.button("Xóa cache demo"):
        clear_demo_cache()
        st.success("Đã xóa cache retrieval/model của demo.")

with right:
    if st.button("Kiểm tra môi trường"):
        st.json(get_runtime_report())
