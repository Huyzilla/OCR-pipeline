from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from .utils import parse_answer_text


class QwenAnswerer:
    def __init__(self, model_name: str, max_new_tokens: int = 16) -> None:
        self.enabled = False
        self.max_new_tokens = max_new_tokens
        self.model_name = model_name
        self.runtime_model_name = model_name
        self.tokenizer = None
        self.model = None
        self.backend = "local"
        self.openai_api_key = os.getenv("OPENAI_KEY") or os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.last_debug: dict = {}

        if self.openai_api_key:
            self.backend = "openai"
            self.runtime_model_name = self.openai_model
            self.enabled = True
            print(f"Using OpenAI API backend with model: {self.runtime_model_name}")
            return

        print(f"Loading LLM: {model_name} ...")
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer

            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype="auto",
                device_map="auto",
            )
            self.enabled = True
        except Exception as e:
            print(f"Warning: cannot load LLM {model_name}. Fallback to non-LLM scoring. Error: {e}")

    def _answer_with_openai(self, system_prompt: str, user_prompt: str) -> str:
        if not self.openai_api_key:
            return ""

        payload = {
            "model": self.runtime_model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0,
            "max_tokens": self.max_new_tokens,
        }

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                response_json = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="ignore")
            except Exception:
                body = ""
            raise RuntimeError(f"OpenAI HTTP {e.code}: {body[:500]}") from e
        except Exception as e:
            raise RuntimeError(f"OpenAI request failed: {e}") from e

        choice = (response_json.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        content = message.get("content", "")
        if isinstance(content, list):
            text_parts: list[str] = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_parts.append(str(part.get("text", "")))
            return "\n".join(text_parts).strip()
        return str(content).strip()

    def answer(self, question: str, options: dict[str, str], contexts: list[str]) -> list[str]:
        if not self.enabled:
            return []

        if self.backend == "local" and (self.model is None or self.tokenizer is None):
            return []

        context_block = "\n\n".join([f"[CTX-{i+1}] {c}" for i, c in enumerate(contexts[:6])])
        options_block = "\n".join([f"{k}. {v}" for k, v in options.items() if v])

        system_prompt = (
            "Bạn là trợ lý giải câu hỏi trắc nghiệm dựa trên CONTEXT.\n"
            "Nhiệm vụ của bạn là chọn đáp án đúng nhất chỉ từ thông tin có trong CONTEXT và trong chính câu hỏi.\n"
            "\n"
            "QUY TẮC CỐT LÕI:\n"
            "1. Chỉ được dùng thông tin xuất hiện trong CONTEXT và trong chính câu hỏi.\n"
            "2. Không được dùng kiến thức bên ngoài, không được bịa thêm dữ kiện, không được tự đặt giả định mới.\n"
            "3. Được phép đối chiếu các cách diễn đạt tương đương, paraphrase gần nghĩa và các diễn đạt lại không làm thay đổi ý chính.\n"
            "4. Được phép thực hiện suy luận ngắn hoặc tính toán đơn giản nếu toàn bộ dữ kiện cần thiết đều xuất hiện trực tiếp trong CONTEXT hoặc trong câu hỏi.\n"
            "5. Các phép được phép gồm: đếm số mục, cộng, trừ, nhân, chia, lấy trung bình, so sánh, suy ra số lượng từ các mốc chỉ số/liệt kê, hoặc các phép biến đổi trực tiếp tương tự.\n"
            "6. Nếu thiếu dữ kiện ở bất kỳ bước nào để suy luận hoặc tính toán, bắt buộc trả về: ANS: ?\n"
            "\n"
            "QUY TẮC CHỌN ĐÁP ÁN:\n"
            "7. Hãy so sánh toàn bộ đáp án và chọn đáp án khớp nhất với ý chính được hỗ trợ bởi CONTEXT.\n"
            "8. Không chọn đáp án chỉ vì có vài từ khóa trùng với CONTEXT nếu nội dung cốt lõi không được hỗ trợ rõ ràng.\n"
            "9. Nếu một đáp án khớp rõ ý chính nhưng có thêm chi tiết phụ không xuất hiện trong CONTEXT, chỉ chọn nếu chi tiết phụ đó không mâu thuẫn với CONTEXT và không làm thay đổi bản chất đáp án.\n"
            "10. Nếu chi tiết phụ làm thay đổi nghĩa, làm hẹp/rộng phạm vi đáng kể, thêm điều kiện quan trọng, hoặc khiến đáp án không còn được CONTEXT hỗ trợ rõ ràng, không được chọn đáp án đó.\n"
            "11. Chỉ chọn nhiều đáp án nếu từng đáp án đều được CONTEXT hỗ trợ rõ ràng và độc lập.\n"
            "12. Không được chọn nhiều đáp án chỉ vì không chắc chắn.\n"
            "13. Không được ưu tiên máy móc đáp án ít hơn hay nhiều hơn; chỉ chọn đúng theo bằng chứng.\n"
            "\n"
            "XỬ LÝ NHIỄU TRONG CÂU HỎI:\n"
            "14. Nếu câu hỏi chứa mã định danh, tên tài liệu, mã học phần, tên gọi phụ, ký hiệu phụ hoặc các thành phần định danh khác mà CONTEXT không có, hãy bỏ qua chúng nếu chúng không ảnh hưởng đến việc trả lời phần ý chính của câu hỏi.\n"
            "15. Chỉ trả về ANS: ? khi không có đáp án nào được hỗ trợ đủ rõ, hoặc khi câu hỏi không thể trả lời chỉ bằng dữ kiện có trong CONTEXT và câu hỏi.\n"
            "\n"
            "CÁCH RA QUYẾT ĐỊNH:\n"
            "16. Trước khi chọn, hãy tự kiểm tra xem đáp án là:\n"
            "   - trích xuất trực tiếp từ CONTEXT,\n"
            "   - suy luận/tính toán trực tiếp từ dữ kiện có sẵn,\n"
            "   - hay cần giả định hoặc kiến thức ngoài.\n"
            "   Chỉ chấp nhận hai loại đầu.\n"
            "\n"
            "ĐỊNH DẠNG TRẢ LỜI:\n"
            "17. Chỉ trả về duy nhất 1 dòng theo đúng một trong các định dạng sau:\n"
            "ANS: A\n"
            "ANS: A,B\n"
            "ANS: A,B,C\n"
            "ANS: A,B,C,D\n"
            "ANS: ?\n"
            "18. Không giải thích, không viết thêm bất kỳ nội dung nào khác ngoài 1 dòng đáp án."
        )

        user_prompt = (
            "Hãy chọn đáp án đúng nhất theo đúng các quy tắc đã được cung cấp.\n"
            "\n"
            "Nhắc lại các ràng buộc quan trọng:\n"
            "- Chỉ dùng thông tin trong CONTEXT và trong chính câu hỏi.\n"
            "- Không dùng kiến thức ngoài, không bịa thêm dữ kiện, không tự đặt giả định.\n"
            "- Được phép tính toán hoặc suy luận ngắn nếu mọi dữ kiện cần thiết đều có sẵn trong CONTEXT hoặc trong câu hỏi.\n"
            "- Chỉ chọn nhiều đáp án nếu từng đáp án đều có căn cứ rõ ràng và độc lập.\n"
            "- Nếu không đủ căn cứ để xác nhận bất kỳ đáp án nào, trả về: ANS: ?\n"
            "- Nếu câu hỏi có chứa mã định danh hoặc tên gọi phụ không ảnh hưởng đến ý chính, hãy bỏ qua chúng.\n"
            "- Chỉ trả về đúng 1 dòng đáp án theo format yêu cầu.\n"
            "\n"
            f"CONTEXT:\n{context_block}\n\n"
            f"QUESTION:\n{question}\n\n"
            f"OPTIONS:\n{options_block}\n"
        )

        self.last_debug = {
            "question": question,
            "options": options,
            "contexts": contexts[:6],
            "context_chars": len(context_block),
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
        }

        if self.backend == "openai":
            text = self._answer_with_openai(system_prompt, user_prompt)
        else:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                top_p=1.0,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.0,
            )
            generated_ids = output_ids[0][inputs["input_ids"].shape[1] :]
            text = self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()

        self.last_debug["raw_output"] = text
        return parse_answer_text(text)
