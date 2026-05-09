#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Answer generation: Qwen 3B với CoT prompt cho tinh_toan
"""

import sys
from pathlib import Path
import os
from typing import TypedDict
try:
    from openai import OpenAI
except ImportError:
    pass

try:
    from qa.utils import parse_answer_text
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from qa.utils import parse_answer_text


class AnswerResult(TypedDict):
    """Kiểu dữ liệu cho answer result"""
    answer: str
    intent: str
    reasoning: str  # Chỉ dùng cho tinh_toan


class AnswerGenerator:
    """
    Tạo answer sử dụng Qwen 3B Instruct
    - tra_cuu: Standard prompt (tìm câu trả lời trực tiếp)
    - tinh_toan: CoT prompt (step-by-step reasoning)
    """
    
    STANDARD_PROMPT = """Dựa vào thông tin sau, trả lời câu hỏi một cách ngắn gọn và chính xác.

CONTEXT:
{context}

QUESTION:
{question}

{options_text}

Chỉ trả về các chữ cái của đáp án đúng (ví dụ: A hoặc A, B). Không giải thích thêm.
ANSWER:"""

    COT_PROMPT = """Dựa vào thông tin sau, giải từng bước rồi trả lời.

CONTEXT:
{context}

QUESTION:
{question}

{options_text}

QUAN TRỌNG:
- Viết số và công thức dạng TEXT THUẦN, KHÔNG dùng LaTeX
- Đúng:  "P = 0.9 * 0.4 / 0.48 = 0.75"
- Sai:   "\\frac{{0.9 \\times 0.4}}{{0.48}}"
- Đúng:  "S_W_inv = [[2/9, -1/9], [-1/9, 5/9]]"
- Sai:   "\\begin{{bmatrix}}...\\end{{bmatrix}}"

Hướng dẫn giải:
Bước 1 - Xác định số liệu: Liệt kê các con số/dữ kiện liên quan trong context
Bước 2 - Tính toán: Thực hiện từng phép tính, ghi rõ công thức
Bước 3 - Đối chiếu: So kết quả với từng đáp án A, B, C, D
Bước 4 - Kết luận: Chọn đáp án đúng

ANSWER:"""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        Initialize answer generator with OpenAI API
        """
        api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        print(f"Answer generator initialized with {model_name} (OpenAI API)")
    
    def _format_options(self, options: dict | None) -> str:
        """Format options thành text"""
        if not options:
            return ""
        
        options_text = "\nOPTIONS:"
        for key, value in options.items():
            if value.strip():
                options_text += f"\n{key}. {value}"
        
        return options_text
    
    def _prepare_prompt(
        self,
        context: str,
        question: str,
        intent: str,
        options: dict | None = None
    ) -> str:
        """Prepare prompt based on intent"""
        options_text = self._format_options(options)
        
        if intent == "tinh_toan":
            prompt = self.COT_PROMPT.format(
                context=context,
                question=question,
                options_text=options_text
            )
        else:  # tra_cuu
            prompt = self.STANDARD_PROMPT.format(
                context=context,
                question=question,
                options_text=options_text
            )
        
        return prompt
    
    def _extract_answer(self, response: str, intent: str) -> tuple[str, str]:
        """
        Extract answer từ response
        
        Args:
            response: Full response từ model
            intent: tra_cuu hoặc tinh_toan
            
        Returns:
            (answer, reasoning)
        """
        # Loại bỏ prompt từ response
        if "ANSWER:" in response:
            answer_part = response.split("ANSWER:")[-1].strip()
        else:
            answer_part = response.strip()
        
        if intent == "tinh_toan":
            # CoT: tìm step-by-step reasoning
            lines = answer_part.split("\n")
            reasoning = answer_part
            
            # Use qa.utils to extract options (e.g. ['A', 'B'])
            parsed = parse_answer_text(answer_part)
            if parsed:
                final_answer = ",".join(parsed)
            else:
                # Fallback if not matching options format
                final_answer = lines[-1].strip() if lines else answer_part
            
            return final_answer, reasoning
        else:
            # tra_cuu: try to parse multiple choice
            parsed = parse_answer_text(answer_part)
            if parsed:
                return ",".join(parsed), ""
            return answer_part, ""
    
    def generate_answer(
        self,
        context: str,
        question: str,
        intent: str,
        options: dict | None = None,
        max_new_tokens: int = 768,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> AnswerResult:
        """
        Generate answer cho question
        
        Args:
            context: Retrieved context
            question: Câu hỏi
            intent: tra_cuu hoặc tinh_toan
            options: Options dict {A: "...", B: "...", ...}
            max_new_tokens: Max tokens để generate
            temperature: Sampling temperature
            top_p: Top-p untuk nucleus sampling
            
        Returns:
            AnswerResult
        """
        prompt = self._prepare_prompt(context, question, intent, options)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Bạn là một chuyên gia trả lời câu hỏi dựa vào tài liệu."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p
            )
            response_text = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"  [WARNING] Answer Generator API Error: {e}")
            response_text = "ANSWER: A" # fallback

        # Extract answer và reasoning
        answer, reasoning = self._extract_answer(response_text, intent)
        
        return {
            "answer": answer,
            "intent": intent,
            "reasoning": reasoning
        }
    
    def __del__(self):
        """Cleanup"""
        pass

def create_answer_generator(model_name: str = "gpt-4o-mini") -> AnswerGenerator:
    """Factory function"""
    return AnswerGenerator(model_name)


if __name__ == "__main__":
    # Test answer generator
    generator = AnswerGenerator()
    
    context = """
    Công ty XYZ có 100 nhân viên. Năm ngoái, họ tuyển thêm 20 nhân viên mới.
    Tỷ lệ giữa nhân viên cũ và nhân viên mới là 4:1.
    """
    
    question = "Năm nay công ty có bao nhiêu nhân viên?"
    options = {
        "A": "80",
        "B": "100",
        "C": "120",
        "D": "140"
    }
    
    # tra_cuu
    print("=== TRA_CUU ===")
    result = generator.generate_answer(
        context=context,
        question=question,
        intent="tra_cuu",
        options=options
    )
    print(f"Answer: {result['answer']}")
    
    # tinh_toan
    print("\n=== TINH_TOAN ===")
    result = generator.generate_answer(
        context=context,
        question=question,
        intent="tinh_toan",
        options=options
    )
    print(f"Answer: {result['answer']}")
    print(f"Reasoning:\n{result['reasoning']}")
