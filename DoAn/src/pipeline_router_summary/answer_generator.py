import os
from typing import TypedDict

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

import torch

from qa.answer_utils import parse_answer

from transformers import AutoTokenizer, AutoModelForCausalLM


class AnswerResult(TypedDict):
    answer:    str
    intent:    str
    reasoning: str   # chỉ có ở tinh_toan


class AnswerGeneratorQwen:

    STANDARD_PROMPT = """Dựa vào thông tin sau đây, vui lòng trả lời câu hỏi.

CONTEXT:
{context}

QUESTION:
{question}

OPTIONS:
{options_text}

Chỉ trả lời đúng 1 dòng, chỉ ghi chữ cái đáp án. Ví dụ: A hoặc AB hoặc ACD
ANSWER:"""

    TRA_CUU_PROMPT = STANDARD_PROMPT

    COT_REASONING_PROMPT = """Dựa vào context sau, phân tích câu hỏi từng bước.

CONTEXT:
{context}

QUESTION:
{question}

OPTIONS:
{options_text}

Phân tích từng bước (KHÔNG cần kết luận đáp án):"""

    TINH_TOAN_COT_PROMPT = COT_REASONING_PROMPT

    COT_ANSWER_PROMPT = """Dựa vào phân tích sau, chọn đáp án đúng.

PHÂN TÍCH:
{reasoning}

QUESTION:
{question}

OPTIONS:
{options_text}

Chỉ trả lời đúng 1 dòng, format: A hoặc AB hoặc ABC hoặc ABCD
ANSWER:"""

    TINH_TOAN_ANSWER_PROMPT = COT_ANSWER_PROMPT

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.model_name = model_name
        self.use_openai = isinstance(model_name, str) and model_name.lower().startswith("gpt")

        if self.use_openai:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise EnvironmentError("OPENAI_API_KEY not set in environment")
            if OpenAI is None:
                raise RuntimeError("openai package not available")
            self.client = OpenAI(api_key=api_key)
            print(f"AnswerGenerator: OpenAI model={model_name}")
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"AnswerGenerator: loading local model {model_name} on {self.device}...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            if self.device == "cuda":
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    low_cpu_mem_usage=True,
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=False,
                )
                self.model = self.model.to(self.device)
            print(f"AnswerGenerator: local model ready on {self.device}")

    def _format_options(self, options: dict | None) -> str:
        if not options:
            return ""
        return "\n".join(
            f"{k}. {options[k]}" for k in ["A", "B", "C", "D"]
            if k in options and str(options[k]).strip()
        )

    def _generate(self, prompt: str, max_new_tokens: int) -> str:
        if self.use_openai:
            try:
                resp = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_new_tokens,
                    temperature=0.0 if max_new_tokens <= 20 else 0.7,
                )
                return resp.choices[0].message.content.strip()
            except Exception as e:
                print(f"  [ERROR] OpenAI generation failed: {e}")
                return ""
        else:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            use_sampling = max_new_tokens > 50
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens  = max_new_tokens,
                    temperature     = 0.7 if use_sampling else 0.0,
                    top_p           = 0.9 if use_sampling else 1.0,
                    do_sample       = use_sampling,
                    pad_token_id    = self.tokenizer.eos_token_id,
                    num_beams       = 1,
                    use_cache       = True,
                )
            return self.tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True,
            ).strip()

    def _extract_answer(self, response: str) -> str:
        _, answer, format_ok = parse_answer(response)
        return answer if format_ok else "X"

    def generate_answer(
        self,
        context:  str,
        question: str,
        intent:   str,
        options:  dict | None = None,
    ) -> AnswerResult:
        options_text = self._format_options(options)
        reasoning    = ""

        if intent == "tinh_toan":
            reasoning = self._generate(
                self.COT_REASONING_PROMPT.format(
                    context=context, question=question, options_text=options_text
                ),
                max_new_tokens=400,
            )
            response = self._generate(
                self.COT_ANSWER_PROMPT.format(
                    reasoning=reasoning, question=question, options_text=options_text
                ),
                max_new_tokens=16,
            )
        else:
            response = self._generate(
                self.STANDARD_PROMPT.format(
                    context=context, question=question, options_text=options_text
                ),
                max_new_tokens=16,
            )

        return {
            "answer":    self._extract_answer(response),
            "intent":    intent,
            "reasoning": reasoning,
        }

    def __del__(self):
        """Cleanup — safe cho cả OpenAI và local model."""
        if hasattr(self, "model"):
            del self.model
        if hasattr(self, "tokenizer"):
            del self.tokenizer
        # Chỉ clear CUDA cache nếu đang dùng local model trên GPU
        if hasattr(self, "device") and self.device == "cuda":
            torch.cuda.empty_cache()


class AnswerGenerator(AnswerGeneratorQwen):
    pass


def create_answer_generator(model_name: str = "gpt-4o-mini") -> AnswerGenerator:
    return AnswerGenerator(model_name)


if __name__ == "__main__":
    context  = "Công ty ABC có 100 nhân viên. Năm ngoái tuyển thêm 20 nhân viên mới."
    question = "Năm nay công ty có bao nhiêu nhân viên?"
    options  = {"A": "80", "B": "100", "C": "120", "D": "140"}

    gen = AnswerGenerator()

    print("\n=== TRA_CUU ===")
    r = gen.generate_answer(context, question, "tra_cuu", options)
    print(f"Answer: {r['answer']}")

    print("\n=== TINH_TOAN ===")
    r = gen.generate_answer(context, question, "tinh_toan", options)
    print(f"Answer: {r['answer']}")
    print(f"Reasoning: {r['reasoning'][:200]}...")
