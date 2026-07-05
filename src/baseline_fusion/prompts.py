from __future__ import annotations


def _format_options(options: list[str]) -> str:
    return "".join(f"{chr(65 + i)}. {opt}\n" for i, opt in enumerate(options) if opt)


STANDARD_PROMPT = """Dựa vào thông tin sau đây, trả lời câu hỏi trắc nghiệm.

CONTEXT:
{context}

QUESTION:
{question}

OPTIONS:
{options_text}
Chỉ trả lời đúng 1 dòng, chỉ ghi chữ cái đáp án (A/B/C/D).
Nếu có nhiều đáp án đúng thì ghi tất cả, ví dụ: AB hoặc ACD.
Không giải thích.
ANSWER:"""


COT_REASONING_PROMPT = """Dựa vào context sau, phân tích câu hỏi từng bước.

CONTEXT:
{context}

QUESTION:
{question}

OPTIONS:
{options_text}
Phân tích từng bước, giữ nguyên số liệu quan trọng. Chưa cần kết luận đáp án cuối cùng:"""


COT_ANSWER_PROMPT = """Dựa vào phân tích sau, chọn đáp án đúng cho câu hỏi trắc nghiệm.

PHÂN TÍCH:
{reasoning}

QUESTION:
{question}

OPTIONS:
{options_text}
Chỉ trả lời đúng 1 dòng, chỉ ghi chữ cái đáp án (A/B/C/D).
Nếu có nhiều đáp án đúng thì ghi tất cả, ví dụ: AB hoặc ACD.
Không giải thích.
ANSWER:"""


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
    return create_standard_answer_prompt(question, context, options)


def create_standard_answer_prompt(question: str, context: str, options: list[str]) -> str:
    return STANDARD_PROMPT.format(
        question=question,
        context=context,
        options_text=_format_options(options),
    )


def create_cot_reasoning_prompt(question: str, context: str, options: list[str]) -> str:
    return COT_REASONING_PROMPT.format(
        question=question,
        context=context,
        options_text=_format_options(options),
    )


def create_cot_answer_prompt(question: str, reasoning: str, options: list[str]) -> str:
    return COT_ANSWER_PROMPT.format(
        question=question,
        reasoning=reasoning,
        options_text=_format_options(options),
    )


def create_fusion_extract_prompt(question: str, context: str) -> str:
    return FUSION_EXTRACT_PROMPT.format(question=question, context=context)
