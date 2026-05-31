#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Giai đoạn 3: Synthesize Hard Negatives từ gold chunks.

Tuân thủ plan:
- 4 loại edit: entity_swap, temporal_edit, logic_flip, provenance_conflict
- Mỗi negative dùng 1 loại edit khác nhau
- Self-check: still_plausible, answers_query, contains_giveaway_style
- Chỉ giữ: still_plausible=true, answers_query=false, contains_giveaway_style=false

Usage:
    python synthesize_negatives_v2.py \
        --judged  domain_data/gold_chunks_judged.jsonl \
        --output  domain_data/synthesized_negatives.jsonl \
        [--resume]
"""

import argparse
import json
import os
import re
import time
from pathlib import Path

from openai import OpenAI

GPT_MODEL   = "gpt-4o-mini"
MAX_TOKENS  = 1000
TEMPERATURE = 0.7
MAX_RETRIES = 5

SYSTEM_PROMPT = """Bạn tạo dữ liệu huấn luyện cho retrieval system.

Với đoạn văn GỐC và query, tạo 2 phiên bản sai lệch tinh vi.
Chọn 2 loại edit PHÙ HỢP NHẤT với nội dung, mỗi version dùng 1 loại khác nhau:

- entity_swap:        đổi thực thể lõi (tên, điều khoản, đối tượng)
- temporal_edit:      đổi số liệu, ngưỡng, mốc thời gian
- logic_flip:         đảo ngược điều kiện, quan hệ nhân quả
- provenance_conflict: đổi phạm vi áp dụng, nguồn tài liệu

Yêu cầu BẮT BUỘC:
- SAO CHÉP TOÀN BỘ đoạn văn gốc, chỉ thay đổi 1-2 chi tiết nhỏ
- KHÔNG rút ngắn, KHÔNG tóm tắt, KHÔNG bỏ câu nào
- Độ dài version phải gần bằng đoạn gốc (±10%)
- KHÔNG thêm câu giveaway như "tuy nhiên...", "thực ra..."
- Mỗi version dùng 1 loại edit khác nhau
- Tự kiểm tra: still_plausible, answers_query, contains_giveaway_style

JSON only:
{
  "version_1": {
    "text": "... (toàn bộ đoạn văn với 1-2 chi tiết đã thay đổi) ...",
    "edit_type": "entity_swap|temporal_edit|logic_flip|provenance_conflict",
    "still_plausible": true,
    "answers_query": false,
    "contains_giveaway_style": false
  },
  "version_2": {
    "text": "... (toàn bộ đoạn văn với 1-2 chi tiết đã thay đổi) ...",
    "edit_type": "entity_swap|temporal_edit|logic_flip|provenance_conflict",
    "still_plausible": true,
    "answers_query": false,
    "contains_giveaway_style": false
  }
}"""

VALID_EDIT_TYPES = {
    "entity_swap", "temporal_edit", "logic_flip", "provenance_conflict"
}


def clean_json_string(raw: str) -> str:
    """Fix common JSON escape issues từ GPT output."""
    # Tìm JSON block
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        return ""
    s = match.group()
    # Fix invalid escapes phổ biến
    s = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', s)
    return s


def validate_version(v: dict, positive: str) -> tuple[bool, str]:
    text = v.get("text", "").strip()

    if not text:
        return False, "empty text"
    if text == positive.strip():
        return False, "identical to positive"
    if len(text) < len(positive) * 0.5:
        return False, f"too short ({len(text)} < {len(positive)*0.5:.0f})"

    edit_type = v.get("edit_type", "")
    valid_aliases = VALID_EDIT_TYPES | {
        "entity", "numeric", "logic", "condition",
        "temporal", "provenance",
    }
    if edit_type and edit_type not in valid_aliases:
        return False, f"invalid edit_type: {edit_type}"

    if v.get("still_plausible") is False:
        return False, "not plausible"
    if v.get("answers_query") is True:
        return False, "still answers query"
    if v.get("contains_giveaway_style") is True:
        return False, "contains giveaway"

    return True, "ok"


def call_gpt(client: OpenAI, positive: str, query: str) -> dict:
    prompt = (f"QUERY: {query[:200]}\n\n"
              f"ĐOẠN VĂN GỐC:\n{positive}\n\n"
              f"Tạo 2 phiên bản sai lệch tinh vi (2 loại edit khác nhau).")

    # MAX_TOKENS động: 2 versions × độ dài positive + JSON overhead
    dynamic_max = min(4000, max(1000, len(positive) * 2 + 500))

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
                max_tokens=dynamic_max,
                temperature=TEMPERATURE,
                timeout=20,
            )
            raw = resp.choices[0].message.content.strip()

            cleaned = clean_json_string(raw)
            if not cleaned:
                return {"error": f"no JSON in response: {raw[:80]}"}

            parsed = json.loads(cleaned)
            return parsed

        except json.JSONDecodeError as e:
            return {"error": f"json: {e}"}
        except Exception as e:
            err_str = str(e)
            if "401" in err_str:
                return {"error": f"auth error"}
            wait = 2 * (2 ** (attempt - 1))
            m = re.search(r'try again in (\d+(?:\.\d+)?)(ms|s)', err_str)
            if m:
                val, unit = float(m.group(1)), m.group(2)
                wait = (val / 1000 if unit == "ms" else val) + 1.5
            if attempt == MAX_RETRIES:
                return {"error": err_str[:80]}
            print(f"    [retry {attempt}] {wait:.1f}s")
            time.sleep(wait)

    return {"error": "max retries"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--judged",  type=Path, required=True)
    parser.add_argument("--output",  type=Path, required=True)
    parser.add_argument("--n",       type=int,  default=0,
                        help="Số câu xử lý (0 = tất cả gold)")
    parser.add_argument("--resume",  action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set"); return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Load gold entries
    print(f"Loading: {args.judged}")
    with open(args.judged, encoding="utf-8") as f:
        all_entries = [json.loads(l) for l in f if l.strip()]

    gold_entries = [
        e for e in all_entries
        if e.get("gold_indices")
        and not e.get("error")
        and e.get("status") != "low_score_skip"
    ]

    if args.n > 0:
        gold_entries = gold_entries[:args.n]

    print(f"  Total judged : {len(all_entries)}")
    print(f"  Gold entries : {len(gold_entries)}")

    # Resume
    done_ids: set[int] = set()
    if args.resume and args.output.exists():
        with open(args.output, encoding="utf-8") as f:
            for line in f:
                done_ids.add(json.loads(line)["index"])
        print(f"  Resume: {len(done_ids)} done")

    client  = OpenAI(api_key=api_key)
    out_f   = open(args.output, "a", encoding="utf-8")

    n_success  = 0
    n_error    = 0
    n_filtered = 0  # valid GPT nhưng fail self-check
    t_start    = time.time()

    for i, entry in enumerate(gold_entries, 1):
        idx      = entry["index"]
        question = entry["question"]
        intent   = entry["intent"]

        if idx in done_ids:
            continue

        # Lấy gold chunk text
        gold_indices = entry["gold_indices"]
        top5         = entry.get("top5_candidates", [])
        gold_chunks  = [
            top5[gi]["chunk"] for gi in gold_indices
            if gi < len(top5) and top5[gi].get("chunk")
        ]

        if not gold_chunks:
            continue

        print(f"  [{i:>4}/{len(gold_entries)}] Q{idx:>4} [{intent:<10}]...",
              end=" ", flush=True)

        # Synthesize cho gold chunk đầu tiên (top-ranked)
        positive = gold_chunks[0]
        raw_result = call_gpt(client, positive, question)

        # Validate từng version
        valid_versions = []
        if not raw_result.get("error"):
            used_edit_types = set()
            for key in ["version_1", "version_2"]:
                v = raw_result.get(key, {})
                if not isinstance(v, dict):
                    continue
                ok, reason = validate_version(v, positive)
                edit_type  = v.get("edit_type", "unknown")

                if edit_type in used_edit_types:
                    n_filtered += 1
                    continue

                if ok:
                    valid_versions.append(v)
                    used_edit_types.add(edit_type)
                else:
                    n_filtered += 1

        out_entry = {
            "index":          idx,
            "question":       question,
            "intent":         intent,
            "positive":       positive,
            "positive_chunk_id": top5[gold_indices[0]]["chunk_id"] if top5 else "",
            "valid_negatives": valid_versions,
            "n_valid":        len(valid_versions),
            "raw_error":      raw_result.get("error"),
        }

        out_f.write(json.dumps(out_entry, ensure_ascii=False) + "\n")
        out_f.flush()

        if raw_result.get("error"):
            n_error += 1
            print(f"ERROR: {raw_result['error'][:60]}")
        elif valid_versions:
            n_success += 1
            types = [v["edit_type"] for v in valid_versions]
            print(f"→ {' + '.join(types)} ({len(valid_versions)} valid)")
        else:
            n_error += 1
            # Log raw để debug
            print(f"NO VALID (filtered={n_filtered})")
            for key in ["version_1", "version_2"]:
                v = raw_result.get(key, {})
                if v:
                    ok, reason = validate_version(v, positive)
                    print(f"    {key}: edit={v.get('edit_type')} "
                          f"plausible={v.get('still_plausible')} "
                          f"answers={v.get('answers_query')} "
                          f"giveaway={v.get('contains_giveaway_style')} "
                          f"→ {reason}")

        if i % 100 == 0:
            elapsed = time.time() - t_start
            per_q   = elapsed / i
            remain  = (len(gold_entries) - i) * per_q
            print(f"    ETA: {remain/60:.1f}min | "
                  f"success={n_success} error={n_error} filtered={n_filtered}")

    out_f.close()

    print(f"\n{'='*55}")
    print(f"DONE: {args.output}")
    print(f"  Success  : {n_success}")
    print(f"  Errors   : {n_error}")
    print(f"  Filtered : {n_filtered} (failed self-check)")
    total_negs = n_success * 2  # estimate
    print(f"  Est. valid negatives: ~{total_negs}")
    cost = (n_success + n_error) * 800 / 1e6 * 0.15
    print(f"  Est. cost: ~${cost:.2f}")


if __name__ == "__main__":
    exit(main())