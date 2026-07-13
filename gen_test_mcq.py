"""
Script tạo prompt sinh câu hỏi MCQ cho bộ test đối chiếu (reconciliation sample).

Mục đích: chọn ngẫu nhiên N tài liệu (trong 50 tài liệu D2), với mỗi tài liệu
sinh sẵn một prompt hoàn chỉnh (kèm nội dung chunk) để dán vào GPT, tạo ra
5-6 câu hỏi trắc nghiệm (tra_cuu + tinh_toan) độc lập với mọi bước tuning
cấu hình reranker/embedding trước đó.
"""

import os
import json
import random
import csv

# ============================== CONFIG ==============================
# Thư mục gốc chứa các folder Public_XXX (mỗi folder có main_chunks_viettel.json)
BASE_DIR = "chunk_outputs1_finals"

# Tên file chunk trong mỗi folder tài liệu
CHUNK_FILENAME = "main_chunks_viettel.json"

# Số tài liệu muốn lấy ngẫu nhiên
N_DOCS = 12

# Số câu hỏi mỗi loại, mỗi tài liệu
TRA_CUU_PER_DOC = 5
TINH_TOAN_PER_DOC = 1

# Nếu một tài liệu có quá nhiều chunk, giới hạn số chunk đưa vào prompt
# (giữ prompt không quá dài, tránh vượt context). Nếu tài liệu có ít hơn
# số này thì dùng hết chunk của tài liệu.
MAX_CHUNKS_PER_DOC = 15

# Seed để có thể tái lập lại đúng bộ tài liệu đã chọn (ghi số này vào đồ án)
RANDOM_SEED = 42

# Thư mục xuất kết quả
OUTPUT_DIR = "reconciliation_test_output"

# Có gọi API GPT tự động không (mặc định KHÔNG — chỉ tạo prompt để bạn tự dán)
USE_API = True
OPENAI_MODEL = "gpt-4o-mini"  # chỉ dùng nếu USE_API=True
# ======================================================================


PROMPT_TEMPLATE = """Bạn là người ra đề thi trắc nghiệm kỹ thuật tiếng Việt, độc lập với bất kỳ hệ thống truy hồi hay AI nào. Nhiệm vụ của bạn là tạo câu hỏi trắc nghiệm để kiểm tra khả năng hiểu tài liệu kỹ thuật của con người, KHÔNG phải để đánh giá một hệ thống máy tính cụ thể.

Dựa trên các đoạn văn bản (chunk) sau đây trích từ tài liệu kỹ thuật "{document_id}", hãy tạo {n_total} câu hỏi trắc nghiệm 4 đáp án (A/B/C/D, chỉ một đáp án đúng).

YÊU CẦU BẮT BUỘC:
- {n_tra_cuu} câu thuộc loại TRA_CUU: câu hỏi có thể trả lời trực tiếp bằng cách tìm thông tin có sẵn trong đoạn văn (định nghĩa, thông số, giá trị, quy trình được nêu rõ).
- {n_tinh_toan} câu thuộc loại TINH_TOAN: câu hỏi yêu cầu lấy từ 2 dữ kiện trở lên trong đoạn văn rồi thực hiện phép tính hoặc suy luận để ra kết quả mới (không có sẵn con số đáp án trong văn bản). Nếu tài liệu không có đủ dữ kiện số liệu để tạo loại này, hãy thay bằng câu tra_cuu và ghi rõ lý do ở cuối.
- KHÔNG diễn đạt câu hỏi bằng cách sao chép nguyên văn cụm từ trong đoạn gold — hãy diễn đạt lại (paraphrase) để câu hỏi giống cách một người dùng thực tế sẽ hỏi, không lộ rõ đáp án nằm ở đâu.
- Với ít nhất 1 câu, hãy cố tình tạo câu hỏi mà thông tin cần thiết nằm rải rác ở nhiều vị trí/đoạn khác nhau trong các chunk được cung cấp (multi-hop), thay vì chỉ nằm gọn trong một câu duy nhất.
- 3 đáp án nhiễu (distractor) phải hợp lý, không được sai một cách hiển nhiên hay vô nghĩa — nên là các giá trị/khái niệm có thật trong tài liệu nhưng không phải đáp án đúng cho câu hỏi này (ví dụ: đúng thông số nhưng sai điều kiện, đúng đơn vị nhưng sai giá trị).
- Không tự đánh giá độ khó hay độ "hợp lý" của câu hỏi khi tạo — chỉ tạo đúng số lượng yêu cầu.

Với mỗi câu hỏi, trả về đúng một object JSON theo cấu trúc sau (trả về một mảng JSON gồm {n_total} object, không kèm text nào khác ngoài JSON):
[
  {{
    "question": "...",
    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "gold_answer": "A/B/C/D",
    "type": "tra_cuu hoặc tinh_toan",
    "source_chunk_index": [chỉ số chunk_index dùng làm nguồn],
    "evidence_quote": "trích đúng câu/đoạn ngắn (dưới 20 từ) trong chunk chứng minh đáp án đúng"
  }}
]

Các đoạn văn bản (mỗi đoạn có chunk_index để bạn tham chiếu ở source_chunk_index):

{chunks_block}
"""


def load_chunks(doc_folder):
    path = os.path.join(BASE_DIR, doc_folder, CHUNK_FILENAME)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def build_chunks_block(chunks):
    parts = []
    for c in chunks:
        idx = c["metadata"].get("chunk_index")
        hier = c["metadata"].get("hierarchy_path", "")
        content = c.get("page_content", "").strip()
        parts.append(f"[chunk_index={idx}] ({hier})\n{content}")
    return "\n\n---\n\n".join(parts)


def main():
    random.seed(RANDOM_SEED)

    if not os.path.isdir(BASE_DIR):
        print(f"KHÔNG tìm thấy thư mục: {BASE_DIR}")
        print("Hãy sửa biến BASE_DIR trong phần CONFIG cho đúng đường dẫn máy bạn.")
        return

    all_doc_folders = sorted(
        d for d in os.listdir(BASE_DIR)
        if os.path.isdir(os.path.join(BASE_DIR, d))
    )
    if len(all_doc_folders) == 0:
        print("Không tìm thấy folder tài liệu nào trong BASE_DIR.")
        return

    n_pick = min(N_DOCS, len(all_doc_folders))
    chosen = sorted(random.sample(all_doc_folders, n_pick))

    out_prompts_dir = os.path.join(OUTPUT_DIR, "prompts")
    os.makedirs(out_prompts_dir, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "answers"), exist_ok=True)

    manifest_rows = []

    for doc_folder in chosen:
        chunks = load_chunks(doc_folder)
        if chunks is None:
            print(f"[Bỏ qua] Không đọc được chunk cho {doc_folder}")
            continue

        # Nếu quá nhiều chunk thì lấy mẫu ngẫu nhiên để prompt không quá dài,
        # nhưng vẫn giữ thứ tự chunk_index cho dễ đọc.
        if len(chunks) > MAX_CHUNKS_PER_DOC:
            sampled = sorted(
                random.sample(chunks, MAX_CHUNKS_PER_DOC),
                key=lambda c: c["metadata"].get("chunk_index", 0)
            )
        else:
            sampled = sorted(chunks, key=lambda c: c["metadata"].get("chunk_index", 0))

        document_id = sampled[0]["metadata"].get("document_id", doc_folder)
        chunks_block = build_chunks_block(sampled)

        n_total = TRA_CUU_PER_DOC + TINH_TOAN_PER_DOC
        prompt = PROMPT_TEMPLATE.format(
            document_id=document_id,
            n_total=n_total,
            n_tra_cuu=TRA_CUU_PER_DOC,
            n_tinh_toan=TINH_TOAN_PER_DOC,
            chunks_block=chunks_block,
        )

        out_path = os.path.join(out_prompts_dir, f"{document_id}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(prompt)

        manifest_rows.append({
            "document_id": document_id,
            "doc_folder": doc_folder,
            "n_chunks_total": len(chunks),
            "n_chunks_used": len(sampled),
            "chunk_indices_used": [c["metadata"].get("chunk_index") for c in sampled],
            "prompt_file": out_path,
        })

        print(f"[OK] {document_id}: {len(sampled)}/{len(chunks)} chunk -> {out_path}")

    manifest_path = os.path.join(OUTPUT_DIR, "manifest.csv")
    with open(manifest_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "document_id", "doc_folder", "n_chunks_total",
            "n_chunks_used", "chunk_indices_used", "prompt_file"
        ])
        writer.writeheader()
        for row in manifest_rows:
            row = dict(row)
            row["chunk_indices_used"] = ";".join(str(i) for i in row["chunk_indices_used"])
            writer.writerow(row)

    print()
    print(f"Đã chọn {len(manifest_rows)} tài liệu (RANDOM_SEED={RANDOM_SEED}).")
    print(f"Manifest: {manifest_path}")
    print(f"Prompts:  {out_prompts_dir}/*.txt")
    print()
    print("Bước tiếp theo:")
    print("1. Mở từng file trong prompts/, dán vào GPT (ChatGPT hoặc API).")
    print("2. Lưu JSON GPT trả về vào answers/<document_id>.json")
    print("3. SINH XONG TOÀN BỘ các tài liệu rồi mới bắt đầu duyệt tay (không duyệt xen kẽ),")
    print("   để tránh lặp lại hiệu ứng feedback loop khi chọn/lọc câu hỏi.")
    print("4. Khi duyệt, đối chiếu 'evidence_quote' với chunk gốc trước khi chấp nhận câu hỏi.")

    if USE_API:
        call_gpt_api(manifest_rows)


def call_gpt_api(manifest_rows):
    """
    Gọi API tự động thay vì copy-paste tay. Cần cài: pip install openai
    và set biến môi trường OPENAI_API_KEY trước khi chạy.
    Chỉ chạy nếu USE_API=True ở phần CONFIG.
    """
    try:
        from openai import OpenAI
    except ImportError:
        print("Chưa cài thư viện openai. Chạy: pip install openai")
        return

    client = OpenAI()  # đọc OPENAI_API_KEY từ biến môi trường
    answers_dir = os.path.join(OUTPUT_DIR, "answers")

    for row in manifest_rows:
        with open(row["prompt_file"], "r", encoding="utf-8") as f:
            prompt = f.read()

        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        text = resp.choices[0].message.content

        out_path = os.path.join(answers_dir, f"{row['document_id']}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[API] {row['document_id']} -> {out_path}")


if __name__ == "__main__":
    main()