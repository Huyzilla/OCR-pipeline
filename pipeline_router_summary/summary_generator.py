#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Summary generator: Tạo summaries cho documents sử dụng GPT-4o mini (OpenAI API)
Thay thế Qwen 2.5 32B Instruct do giới hạn tài nguyên.
"""

import json
import os
from pathlib import Path
from typing import TypedDict
from tqdm import tqdm

try:
    from openai import OpenAI
except ImportError:
    raise ImportError(
        "Thiếu thư viện openai. Cài đặt bằng: pip install openai"
    )


class DocumentSummary(TypedDict):
    """Kiểu dữ liệu cho document summary"""
    doc_id: str
    summary_text: str
    chunk_count: int
    token_count: int


class SummaryGenerator:
    """
    Tạo summaries cho documents sử dụng GPT-4o mini qua OpenAI API.
    API key được load từ biến môi trường OPENAI_API_KEY.
    """

    SUMMARY_PROMPT_TEMPLATE = """Tạo một summary ngắn gọn (150-200 từ) cho document sau.

Yêu cầu format:
- Chỉ dùng text thuần. Không dùng markdown bold (**) hay heading (#).
- Dòng 1: Chủ đề chính (1 câu)
- Dòng 2: Các khái niệm/thuật ngữ chính (liệt kê, cách nhau bằng dấu phẩy)
- Dòng 3: Loại nội dung (ví dụ: lý thuyết / thực hành / quy định / nghiên cứu)

Document content:
{content}

Summary:"""

    # Giới hạn ký tự content trước khi gửi lên API (tránh tốn token)
    MAX_CONTENT_CHARS: int = 6000

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        Initialize summary generator với OpenAI API.

        Args:
            model_name: Tên model OpenAI, mặc định là "gpt-4o-mini"
        """
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "Biến môi trường OPENAI_API_KEY chưa được thiết lập. "
                "Thêm OPENAI_API_KEY vào file .env hoặc export trước khi chạy."
            )

        self.model_name = model_name
        self.client = OpenAI(api_key=api_key)
        print(f"Summary generator initialized: model={model_name} (OpenAI API)")

    def _prepare_content(self, content: str) -> str:
        """
        Chuẩn bị nội dung gửi lên API.
        - Nếu ngắn hơn MAX_CONTENT_CHARS: gửi hết
        - Nếu dài hơn: lấy mẫu phân bố đều (đầu + giữa + cuối)
          để GPT nhìn toàn bộ document, không chỉ phần đầu.
        """
        if len(content) <= self.MAX_CONTENT_CHARS:
            return content

        # Stratified sampling: 30% đầu + 40% giữa + 30% cuối
        limit = self.MAX_CONTENT_CHARS
        head = content[:int(limit * 0.30)]
        mid_start = (len(content) - int(limit * 0.40)) // 2
        mid = content[mid_start: mid_start + int(limit * 0.40)]
        tail = content[-int(limit * 0.30):]

        return (
            head
            + "\n\n...[middle section]...\n\n"
            + mid
            + "\n\n...[end section]...\n\n"
            + tail
        )

    def generate_summary(self, doc_id: str, content: str, chunk_count: int = 0) -> DocumentSummary:
        """
        Tạo summary cho một document qua OpenAI API.

        Args:
            doc_id: ID của document
            content: Nội dung của document
            chunk_count: Số chunks trong document

        Returns:
            DocumentSummary chứa summary text
        """
        if not content.strip():
            return {
                "doc_id": doc_id,
                "summary_text": f"Document {doc_id}: Nội dung trống",
                "chunk_count": chunk_count,
                "token_count": 0
            }

        truncated_content = self._prepare_content(content)
        user_prompt = self.SUMMARY_PROMPT_TEMPLATE.format(content=truncated_content)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Bạn là trợ lý tóm tắt tài liệu chuyên nghiệp, "
                            "viết summary ngắn gọn, rõ ràng bằng tiếng Việt."
                        )
                    },
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.7,
            )
        except Exception as e:
            print(f"  [WARNING] OpenAI API error for {doc_id}: {e}")
            return {
                "doc_id": doc_id,
                "summary_text": f"Document {doc_id}: Không thể tạo summary ({e})",
                "chunk_count": chunk_count,
                "token_count": 0
            }

        summary_text = response.choices[0].message.content.strip()
        # Token count từ response usage
        token_count = response.usage.completion_tokens if response.usage else len(summary_text.split())

        return {
            "doc_id": doc_id,
            "summary_text": summary_text,
            "chunk_count": chunk_count,
            "token_count": token_count
        }

    def generate_summaries_batch(
        self,
        documents: dict[str, str],
        output_json: Path | None = None
    ) -> list[DocumentSummary]:
        """
        Tạo summaries cho batch documents.

        Args:
            documents: Dict {doc_id: content}
            output_json: Path để lưu output JSON

        Returns:
            Danh sách DocumentSummary
        """
        summaries: list[DocumentSummary] = []

        print(f"Generating summaries for {len(documents)} documents (model: {self.model_name})...")
        for doc_id, content in tqdm(documents.items(), desc="Generating summaries"):
            chunk_count = len(content.split("\n\n"))  # Rough estimate
            summary = self.generate_summary(doc_id, content, chunk_count)
            summaries.append(summary)

        if output_json:
            output_json.parent.mkdir(parents=True, exist_ok=True)
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(summaries, f, ensure_ascii=False, indent=2)
            print(f"Summaries saved to {output_json}")

        return summaries


def create_summary_generator(model_name: str = "gpt-4o-mini") -> SummaryGenerator:
    """Factory function để tạo summary generator"""
    return SummaryGenerator(model_name)


if __name__ == "__main__":
    # Test summary generator
    # Đảm bảo OPENAI_API_KEY đã được set trong .env hoặc environment
    from dotenv import load_dotenv
    load_dotenv()

    generator = SummaryGenerator()

    test_documents = {
        "Public001": """
        Chính sách lương và phúc lợi của công ty.
        Lương được trả hàng tháng vào ngày 25.
        Phúc lợi bao gồm: Bảo hiểm y tế, bảo hiểm thất nghiệt, hỗ trợ tiền ăn trưa.
        Nhân viên được hưởng 15 ngày phép/năm, được tăng lương hàng năm.
        """,
        "Public002": """
        Quy trình tuyển dụng và onboarding nhân sự.
        Ứng viên cần nộp CV và thư xin việc.
        Vòng 1: Phỏng vấn HR, Vòng 2: Phỏng vấn chuyên môn.
        Nếu vượt qua, sẽ nhận offer letter và tiến hành onboarding.
        """
    }

    summaries = generator.generate_summaries_batch(
        test_documents,
        output_json=Path("test_summaries.json")
    )

    print("\nGenerated summaries:")
    for s in summaries:
        print(f"\nDoc: {s['doc_id']}")
        print(f"Tokens: {s['token_count']}")
        print(f"Summary: {s['summary_text'][:100]}...")
