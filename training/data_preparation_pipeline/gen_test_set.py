import json
import time
from pathlib import Path
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

SCRIPT_DIR = Path(__file__).resolve().parent


def find_repo_root(start: Path) -> Path:
    for path in (start, *start.parents):
        if (path / ".git").exists():
            return path
    return start.parents[1]


ROOT_DIR = find_repo_root(SCRIPT_DIR)
CHUNK_DIR_CANDIDATES = [
    ROOT_DIR / "chunk_outputs1_finals",
    ROOT_DIR / "chunk_outputs1_final",
]
OUTPUT_PATH = SCRIPT_DIR / "question_btc_style.jsonl"

BTC_EXAMPLES = [
    {
        "question": "Trong mô hình nhà thông minh, IoT chủ yếu đóng vai trò gì?",
        "A": "Lưu trữ dữ liệu trên đám mây",
        "B": "Kết nối internet và quản lý từ xa các thiết bị",
        "C": "Phân tích dữ liệu lớn",
        "D": "Cung cấp giao diện người dùng",
        "answer": "B"
    },
    {
        "question": "Điểm BLEU dùng để đánh giá chất lượng của hệ thống nào?",
        "A": "Hệ thống nhận diện giọng nói",
        "B": "Hệ thống dịch máy",
        "C": "Hệ thống phân loại ảnh",
        "D": "Hệ thống gợi ý sản phẩm",
        "answer": "B"
    },
]

def build_prompt(chunk_text: str) -> str:
    examples_str = json.dumps(BTC_EXAMPLES, ensure_ascii=False, indent=2)
    return f"""Dưới đây là ví dụ câu hỏi trắc nghiệm học thuật tiếng Việt:
{examples_str}

Dựa trên đoạn văn sau, tạo 1 câu hỏi trắc nghiệm tương tự:

Đoạn văn:
{chunk_text[:800]}

Yêu cầu:
- Câu hỏi ngắn gọn, hỏi về khái niệm/vai trò/đặc điểm
- Không trích nguyên văn từ đoạn văn
- 4 đáp án A/B/C/D, chỉ 1 đáp án đúng
- Đáp án đúng phải có trong đoạn văn
- 3 đáp án sai phải hợp lý (không quá dễ loại)

Trả về JSON theo format sau, không giải thích thêm:
{{
  "question": "...",
  "A": "...",
  "B": "...",
  "C": "...",
  "D": "...",
  "answer": "A|B|C|D"
}}"""


# ── Load data ─────────────────────────────────────────────────────────────────
def resolve_chunk_dir() -> Path:
    for chunk_dir in CHUNK_DIR_CANDIDATES:
        if chunk_dir.exists():
            return chunk_dir
    tried = ", ".join(str(path) for path in CHUNK_DIR_CANDIDATES)
    raise FileNotFoundError(f"Chunk directory not found. Tried: {tried}")


def load_chunk_corpus(chunk_dir: Path) -> dict[str, str]:
    chunk_files = sorted(chunk_dir.glob("*/*_chunks*.json"))
    if not chunk_files:
        chunk_files = sorted(chunk_dir.glob("*/*.json"))
    if not chunk_files:
        raise FileNotFoundError(f"No chunk JSON files found under {chunk_dir}")

    corpus = {}
    for chunk_file in chunk_files:
        doc_scope = chunk_file.parent.name
        with open(chunk_file, encoding="utf-8") as f:
            records = json.load(f)

        if not isinstance(records, list):
            continue

        for i, item in enumerate(records):
            if not isinstance(item, dict):
                continue

            chunk_text = str(item.get("page_content", "")).strip()
            if not chunk_text:
                continue

            metadata = item.get("metadata", {})
            metadata = metadata if isinstance(metadata, dict) else {}
            raw_chunk_id = metadata.get("chunk_id") or f"chunk::{metadata.get('chunk_index', i)}"
            raw_chunk_id = str(raw_chunk_id).strip()
            if not raw_chunk_id:
                continue

            if raw_chunk_id.startswith(f"{doc_scope}::"):
                chunk_id = raw_chunk_id
            else:
                chunk_id = f"{doc_scope}::{raw_chunk_id}"

            corpus[chunk_id] = chunk_text

    return corpus


chunk_dir = resolve_chunk_dir()
corpus = load_chunk_corpus(chunk_dir)

print(f"Corpus: {len(corpus)} chunks from {chunk_dir}")

# ── Generate ──────────────────────────────────────────────────────────────────
results, skipped = [], 0

for i, (chunk_id, chunk_text) in enumerate(corpus.items(), 1):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": build_prompt(chunk_text)}],
            temperature=0.7,
            max_tokens=300,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content.strip()
        mcq = json.loads(raw)

        # Validate
        if not all(k in mcq for k in ["question","A","B","C","D","answer"]):
            skipped += 1
            continue
        if mcq["answer"] not in ["A","B","C","D"]:
            skipped += 1
            continue

        results.append({
            **mcq,
            "gold_chunk_ids": [chunk_id],
            "source_chunk_id": chunk_id,
        })

        if i % 50 == 0:
            print(f"  {i}/{len(corpus)} chunks done | generated {len(results)}")

        time.sleep(0.1)

    except Exception as e:
        print(f"  Error {i} ({chunk_id}): {e}")
        skipped += 1

# ── Save ──────────────────────────────────────────────────────────────────────
out = OUTPUT_PATH
with open(out, "w", encoding="utf-8") as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"\nSaved: {len(results)} | Skipped: {skipped}")
if results:
    print(f"\nSample:\n{json.dumps(results[0], ensure_ascii=False, indent=2)}")
