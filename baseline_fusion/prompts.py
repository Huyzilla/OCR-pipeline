from __future__ import annotations


FUSION_EXTRACT_PROMPT = """Dưới đây là các đoạn tài liệu liên quan đến một câu hỏi.
Hãy trích rút và tóm tắt CHỈ những thông tin cần thiết để trả lời câu hỏi.
Giữ nguyên số liệu, tên riêng, thuật ngữ quan trọng. Bỏ phần không liên quan.
Trả lời bằng tiếng Việt, tối đa 300 từ.

QUESTION:
{question}

DOCUMENTS:
{context}

TRÍCH RÚT:"""


def create_answer_prompt(question: str, context: str, options: list[str]) -> str:
    opts = "".join(f"{chr(65 + i)}. {opt}\n" for i, opt in enumerate(options) if opt)
    return (
        "Dựa vào thông tin sau đây, trả lời câu hỏi trắc nghiệm.\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION:\n{question}\n\n"
        f"OPTIONS:\n{opts}\n"
        "Chỉ trả lời đúng 1 dòng, chỉ ghi chữ cái đáp án (A/B/C/D). "
        "Nếu có nhiều đáp án đúng thì ghi tất cả, ví dụ: AB hoặc ACD. "
        "Không giải thích.\n"
        "ANSWER:"
    )


def create_fusion_extract_prompt(question: str, context: str) -> str:
    return FUSION_EXTRACT_PROMPT.format(question=question, context=context)
