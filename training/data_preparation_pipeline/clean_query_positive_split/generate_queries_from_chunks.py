from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
from pathlib import Path
from typing import Any

from openai import OpenAI


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = SCRIPT_DIR / "chunks_not_in_train_or_eval.jsonl"
DEFAULT_OUTPUT = SCRIPT_DIR / "generated_query_positive_from_uncovered.jsonl"

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_N_QUESTIONS = 2
MAX_RETRIES = 5

SYSTEM_PROMPT = """Bạn tạo dữ liệu query-positive cho hệ thống truy hồi tài liệu.

Nhiệm vụ: đọc một đoạn văn pháp lý/kỹ thuật và viết các câu hỏi mà người dùng thật có thể gõ để tìm đoạn đó.
Luôn trả về JSON hợp lệ, không giải thích thêm."""


def find_repo_root(start: Path) -> Path:
    for path in (start, *start.parents):
        if (path / ".git").exists():
            return path
    return start


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def iter_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSONL: {exc}") from exc
    return rows


def done_chunk_ids(output_path: Path) -> set[str]:
    if not output_path.exists():
        return set()

    done: set[str] = set()
    with output_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            chunk_id = obj.get("positive_chunk_id")
            if chunk_id:
                done.add(str(chunk_id))
    return done


def clean_json_object(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return ""
    return match.group(0)


def build_prompt(chunk_text: str, n_questions: int) -> str:
    return f"""Bạn là người dùng đang tra cứu tài liệu pháp lý/kỹ thuật. Đọc đoạn văn sau và đặt câu hỏi mà đoạn này trả lời được.

ĐOẠN VĂN:
{chunk_text}

YÊU CẦU:
- Đặt {n_questions} câu hỏi KHÁC NHAU mà đoạn văn trên trả lời được.
- Viết như người dùng thật gõ tìm kiếm: ngắn gọn, tự nhiên. KHÔNG "xin vui lòng", KHÔNG trang trọng.
- QUAN TRỌNG: KHÔNG sao chép nguyên cụm từ dài trong đoạn văn. Diễn đạt lại bằng từ ngữ của bạn, dùng từ đồng nghĩa. Câu hỏi và đoạn văn KHÔNG được trùng lặp nhiều từ khóa.
- Câu hỏi phải trả lời được CHỈ bằng đoạn văn này, không cần thông tin ngoài.
- Nếu đoạn văn có số liệu/công thức/điều kiện tính toán, đặt ít nhất 1 câu hỏi dạng tính toán/áp dụng.
- Nếu đoạn văn quá ngắn/không có nội dung đáng hỏi (mục lục, tiêu đề, bảng trống), trả về danh sách rỗng.

Trả về JSON:
{{"questions": ["câu hỏi 1", "câu hỏi 2"], "chunk_quality": "good" | "low"}}"""


def infer_intent(question: str, chunk_text: str) -> str:
    text = f"{question}\n{chunk_text}".lower()
    if re.search(r"\b(tính|tính toán|bao nhiêu|công thức|xác định|áp dụng|chu kỳ|diện tích|thể tích)\b", text):
        if re.search(r"\d|=|\+|-|\*|/|%|π|sqrt|sin|cos|log", text):
            return "tinh_toan"
    return "tra_cuu"


def normalize_questions(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    questions: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            continue
        question = re.sub(r"\s+", " ", item).strip()
        question = question.strip('"').strip("'")
        if not question:
            continue
        key = question.casefold()
        if key in seen:
            continue
        seen.add(key)
        questions.append(question)
    return questions


def call_model(client: OpenAI, model: str, chunk_text: str, n_questions: int) -> dict[str, Any]:
    prompt = build_prompt(chunk_text, n_questions)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=max(350, 120 * n_questions),
                response_format={"type": "json_object"},
                timeout=60,
            )
            raw = response.choices[0].message.content or ""
            cleaned = clean_json_object(raw)
            if not cleaned:
                return {"error": f"no JSON object in response: {raw[:120]}"}
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            return {"error": f"invalid JSON: {exc}"}
        except Exception as exc:
            error = str(exc)
            if "401" in error:
                return {"error": "auth error: check OPENAI_API_KEY"}
            if attempt >= MAX_RETRIES:
                return {"error": error[:300]}

            wait = min(60.0, 2.0 * (2 ** (attempt - 1))) + random.random()
            retry_after = re.search(r"try again in (\d+(?:\.\d+)?)(ms|s)", error)
            if retry_after:
                value = float(retry_after.group(1))
                wait = value / 1000.0 if retry_after.group(2) == "ms" else value
                wait += 1.0
            print(f"  retry {attempt}/{MAX_RETRIES} after {wait:.1f}s: {error[:120]}")
            time.sleep(wait)

    return {"error": "max retries"}


def write_jsonl_line(handle, record: dict[str, Any]) -> None:
    handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    handle.flush()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--n", type=int, default=DEFAULT_N_QUESTIONS, help="questions per good chunk")
    parser.add_argument("--limit", type=int, default=0, help="process only the first N pending chunks")
    parser.add_argument("--offset", type=int, default=0, help="skip this many input chunks before processing")
    parser.add_argument("--resume", action="store_true", help="skip chunks already present in output")
    parser.add_argument("--keep-low-quality", action="store_true", help="write low-quality chunks with empty questions")
    parser.add_argument("--sleep", type=float, default=0.1, help="seconds to sleep after each chunk")
    parser.add_argument("--dry-run", action="store_true", help="print counts and prompt sample without calling the API")
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("--n must be >= 1")

    repo_root = find_repo_root(SCRIPT_DIR)
    load_dotenv(repo_root / ".env")

    rows = iter_jsonl(args.input)
    rows = rows[args.offset :]
    if args.limit > 0:
        rows = rows[: args.limit]

    done = done_chunk_ids(args.output) if args.resume else set()
    pending = [row for row in rows if str(row.get("chunk_id", "")) not in done]

    print(f"Input chunks : {len(rows)}")
    print(f"Resume done  : {len(done)}")
    print(f"Pending      : {len(pending)}")
    print(f"Output       : {args.output}")
    print(f"Model        : {args.model}")
    print(f"Questions/chunk: {args.n}")

    if args.dry_run:
        if pending:
            sample_text = str(pending[0].get("page_content", ""))
            print("\n--- prompt sample ---")
            print(build_prompt(sample_text[:2000], args.n))
        return 0

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is not set. Put it in the environment or .env.", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    client = OpenAI(api_key=api_key)

    mode = "a" if args.resume and args.output.exists() else "w"
    n_chunks_good = 0
    n_chunks_low = 0
    n_questions = 0
    n_errors = 0

    with args.output.open(mode, encoding="utf-8") as out_f:
        for index, chunk in enumerate(pending, 1):
            chunk_id = str(chunk.get("chunk_id", "")).strip()
            chunk_text = str(chunk.get("page_content", "")).strip()
            print(f"[{index}/{len(pending)}] {chunk_id}")

            if not chunk_id or not chunk_text:
                n_errors += 1
                print("  skip: missing chunk_id or page_content")
                continue

            result = call_model(client, args.model, chunk_text, args.n)
            if result.get("error"):
                n_errors += 1
                write_jsonl_line(
                    out_f,
                    {
                        "chunk_id": chunk_id,
                        "error": result["error"],
                        "source": "generate_queries_from_chunks.py",
                    },
                )
                print(f"  error: {result['error']}")
                continue

            quality = str(result.get("chunk_quality", "low")).strip().lower()
            questions = normalize_questions(result.get("questions"))
            if quality not in {"good", "low"}:
                quality = "low"

            if quality == "low" or not questions:
                n_chunks_low += 1
                if args.keep_low_quality:
                    write_jsonl_line(
                        out_f,
                        {
                            "chunk_id": chunk_id,
                            "positive": chunk_text,
                            "positive_chunk_id": chunk_id,
                            "chunk_quality": quality,
                            "questions": questions,
                            "source_file": chunk.get("source_file"),
                            "metadata": chunk.get("metadata"),
                            "source": "generate_queries_from_chunks.py",
                        },
                    )
                print(f"  low quality, questions={len(questions)}")
                continue

            n_chunks_good += 1
            for q_idx, question in enumerate(questions[: args.n], 1):
                record = {
                    "query": question,
                    "positive": chunk_text,
                    "positive_chunk_id": chunk_id,
                    "intent": infer_intent(question, chunk_text),
                    "chunk_quality": quality,
                    "question_index": q_idx,
                    "source_file": chunk.get("source_file"),
                    "metadata": chunk.get("metadata"),
                    "source": "generate_queries_from_chunks.py",
                }
                write_jsonl_line(out_f, record)
                n_questions += 1
            print(f"  wrote {min(len(questions), args.n)} questions")

            if args.sleep > 0:
                time.sleep(args.sleep)

    print("\nDone")
    print(f"  good chunks : {n_chunks_good}")
    print(f"  low chunks  : {n_chunks_low}")
    print(f"  questions   : {n_questions}")
    print(f"  errors      : {n_errors}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
