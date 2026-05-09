#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Router module: Intent detection + Public ID extraction
Sử dụng Qwen2.5 1.5B Instruct local để phân loại intent: tra_cuu / tinh_toan
"""

import re
from typing import TypedDict

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    from qa.utils import detect_public_doc_ids
except ImportError:
    detect_public_doc_ids = None


class RouterResult(TypedDict):
    """Result từ router"""
    question: str
    intent: str  # "tra_cuu" hoặc "tinh_toan"
    public_ids: list[str]  # Danh sách public_id tìm được
    has_public_id: bool  # True nếu có public_id


class QuestionRouter:
    """
    Router để phân loại intent câu hỏi
    - tra_cuu: Tra cứu thông tin, định nghĩa, giải thích
    - tinh_toan: Bài toán tính toán, yêu cầu phép tính
    """
    
    ROUTER_PROMPT_TEMPLATE = """Phân loại intent của câu hỏi sau. Trả lời chỉ một từ:
- "tra_cuu" nếu câu hỏi yêu cầu tra cứu, tìm kiếm thông tin, định nghĩa, giải thích
- "tinh_toan" nếu câu hỏi yêu cầu tính toán, giải bài toán

Câu hỏi: {question}

Intent: """

    # Pattern fallback để tìm public_id dạng Public_001/Public-001/Public 1
    PUBLIC_ID_FALLBACK_PATTERN = r'\bpublic[_\s-]?(\d{1,3})\b'
    
    def __init__(self, model_name: str = "Qwen/Qwen2.5-1.5B-Instruct"):
        """
        Initialize router với model local Qwen2.5 1.5B Instruct
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"Loading router model: {model_name}")
        print(f"Router device: {self.device}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
        )

        if self.device == "cpu":
            self.model = self.model.to(self.device)

        self.model.eval()
        print(f"Router initialized with local model {model_name}")
    
    def extract_public_ids(self, text: str) -> list[str]:
        """
        Trích xuất public_id từ text
        
        Args:
            text: Text để tìm public_id
            
        Returns:
            Danh sách public_id tìm được
        """
        if detect_public_doc_ids is not None:
            return detect_public_doc_ids(text)

        matches = re.findall(self.PUBLIC_ID_FALLBACK_PATTERN, text, flags=re.IGNORECASE)
        # Giữ thứ tự xuất hiện và chuẩn hóa thành PublicNNN
        ordered_unique = []
        seen = set()
        for m in matches:
            doc_id = f"Public{int(m):03d}"
            if doc_id not in seen:
                seen.add(doc_id)
                ordered_unique.append(doc_id)
        return ordered_unique
    
    def detect_intent(self, question: str) -> str:
        """
        Phát hiện intent của câu hỏi
        
        Args:
            question: Câu hỏi cần phân loại
            
        Returns:
            "tra_cuu" hoặc "tinh_toan"
        """
        prompt = self.ROUTER_PROMPT_TEMPLATE.format(question=question)
        try:
            messages = [
                {"role": "system", "content": "Bạn là một trợ lý thông minh phân loại câu hỏi. Chỉ trả về một từ duy nhất: 'tra_cuu' hoặc 'tinh_toan'."},
                {"role": "user", "content": prompt},
            ]

            if hasattr(self.tokenizer, "apply_chat_template"):
                input_text = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                )
            else:
                input_text = f"{messages[0]['content']}\n\n{messages[1]['content']}\n\nAssistant:"

            inputs = self.tokenizer(input_text, return_tensors="pt")
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=8,
                    temperature=0.0,
                    do_sample=False,
                    top_p=1.0,
                    pad_token_id=self.tokenizer.eos_token_id,
                )

            response_text = self.tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True
            ).strip()
        except Exception as e:
            print(f"  [WARNING] Router model error: {e}")
            response_text = "tra_cuu"

        # Parse response để lấy intent
        response_lower = response_text.lower().strip()
        if "tinh_toan" in response_lower or "tính toán" in response_lower:
            return "tinh_toan"
        elif "tra_cuu" in response_lower or "tra cứu" in response_lower:
            return "tra_cuu"
        else:
            # Default fallback: kiểm tra các từ khóa
            if any(kw in question.lower() for kw in ["tính", "tính toán", "bao nhiêu", "cộng", "trừ", "nhân", "chia"]):
                return "tinh_toan"
            return "tra_cuu"
    
    def route(self, question: str) -> RouterResult:
        """
        Route câu hỏi: phân loại intent + trích xuất public_id
        
        Args:
            question: Câu hỏi cần route
            
        Returns:
            RouterResult chứa intent, public_ids, có_public_id
        """
        intent = self.detect_intent(question)
        public_ids = self.extract_public_ids(question)
        has_public_id = len(public_ids) > 0
        
        return {
            "question": question,
            "intent": intent,
            "public_ids": public_ids,
            "has_public_id": has_public_id
        }
    
    def __del__(self):
        """Cleanup"""
        pass

# Hàm helper để sử dụng router
def create_router(model_name: str = "gpt-4o-mini") -> QuestionRouter:
    """Factory function để tạo router"""
    return QuestionRouter(model_name)


if __name__ == "__main__":
    # Test router
    router = QuestionRouter()
    
    test_questions = [
        "Tính 123 + 456 = ?",
        "Public001 nói gì về định nghĩa?",
        "Giải bài toán: 2x + 3 = 7, tìm x",
        "Tìm thông tin về chính sách trong Public002"
    ]
    
    for q in test_questions:
        result = router.route(q)
        print(f"Q: {q}")
        print(f"Intent: {result['intent']}, Public IDs: {result['public_ids']}")
        print()
