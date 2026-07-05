#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Giai đoạn 2: GPT judge xác định gold chunks từ retrieve_rerank_991.jsonl

Với mỗi query, gửi top-5 candidates cho GPT judge:
→ GPT trả về gold_indices, partial_indices, irrelevant_indices, confidence

Output: gold_chunks_judged.jsonl

Usage:
    # Chạy 500 câu đầu
    python gpt_judge_gold_chunks.py \
        --input    retrieve_rerank_991.jsonl \
        --output   domain_data/gold_chunks_judged.jsonl \
        --n        500 \
        [--resume]

    # Chạy tiếp 500 câu còn lại
    python gpt_judge_gold_chunks.py \
        --input    retrieve_rerank_991.jsonl \
        --output   domain_data/gold_chunks_judged.jsonl \
        --offset   500 \
        --n        500 \
        [--resume]

    # Chạy tất cả
    python gpt_judge_gold_chunks.py \
        --input    retrieve_rerank_991.jsonl \
        --output   domain_data/gold_chunks_judged.jsonl
"""

import argparse
import json
import os
import re
import time
from pathlib import Path

from openai import OpenAI

GPT_MODEL   = "gpt-4o-mini"
MAX_TOKENS  = 100
TEMPERATURE = 0
MAX_RETRIES = 5
TOP_K_JUDGE = 5   # chỉ gửi top-5 cho GPT


SYSTEM_PROMPT = """Judge relevance cho RAG tiếng Việt.

Phân loại từng chunk:
- gold: đủ thông tin trả lời trực tiếp
- partial: liên quan nhưng không đủ
- irrelevant: không liên quan

JSON only:
{"gold_indices": [...], "partial_indices": [...], "irrelevant_indices": [...], "confidence": "high|medium|low"}"""


def build_prompt(question: str, intent: str, candidates: list[dict]) -> str:
    chunks_text = ""
    for i, c in enumerate(candidates[:TOP_K_JUDGE]):
        text = c.get("chunk", "")[:800]
        chunks_text += f"\n[CHUNK_{i}] (bge_score={c.get('bge_score',0):.3f})\n{text}\n"

    return (f"QUERY: {question}\n"
            f"INTENT: {intent}\n"
            f"\nCÁC ĐOẠN VĂN:{chunks_text}\n"
            f"Phân loại từng chunk.")


def call_gpt(client: OpenAI, question: str,
             intent: str, candidates: list[dict]) -> dict | None:
    prompt = build_prompt(question, intent, candidates)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
            )
            raw = resp.choices[0].message.content.strip()

            # Parse JSON
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if not match:
                return {"error": f"no JSON: {raw[:100]}"}

            parsed = json.loads(match.group())

            # Validate indices
            n = min(len(candidates), TOP_K_JUDGE)
            for key in ["gold_indices", "partial_indices", "irrelevant_indices"]:
                parsed[key] = [i for i in parsed.get(key, [])
                               if isinstance(i, int) and 0 <= i < n]

            parsed["raw"] = raw
            return parsed

        except json.JSONDecodeError as e:
            return {"error": f"json parse: {e}", "raw": raw[:200]}
        except Exception as e:
            wait = 2 * (2 ** (attempt - 1))
            m = re.search(r'try again in (\d+(?:\.\d+)?)(ms|s)', str(e))
            if m:
                val, unit = float(m.group(1)), m.group(2)
                wait = (val / 1000 if unit == "ms" else val) + 1.5
            if attempt == MAX_RETRIES:
                return {"error": str(e)[:100]}
            print(f"    [retry {attempt}] {wait:.1f}s")
            time.sleep(wait)

    return {"error": "max retries"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",   type=Path, required=True,
                        help="retrieve_rerank_991.jsonl")
    parser.add_argument("--output",  type=Path, required=True,
                        help="gold_chunks_judged.jsonl")
    parser.add_argument("--n",       type=int,  default=0,
                        help="Số câu chạy (0 = tất cả)")
    parser.add_argument("--offset",  type=int,  default=0,
                        help="Bỏ qua N câu đầu trong input")
    parser.add_argument("--resume",  action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Load input
    print(f"Loading: {args.input}")
    with open(args.input, encoding="utf-8") as f:
        all_entries = [json.loads(l) for l in f if l.strip()]
    print(f"  Total entries in file: {len(all_entries)}")

    # Apply offset + limit
    entries = all_entries[args.offset:]
    if args.n > 0:
        entries = entries[:args.n]
    print(f"  Will process: {len(entries)} entries "
          f"(offset={args.offset}, n={args.n if args.n > 0 else 'all'})")

    # Resume: load đã xử lý
    done_ids: set[int] = set()
    if args.resume and args.output.exists():
        with open(args.output, encoding="utf-8") as f:
            for line in f:
                done_ids.add(json.loads(line)["index"])
        print(f"  Resume: {len(done_ids)} already done")

    # Run
    client  = OpenAI(api_key=api_key)
    out_f   = open(args.output, "a", encoding="utf-8")

    n_gold      = 0
    n_none      = 0
    n_error     = 0
    n_review    = 0
    t_start     = time.time()

    for i, entry in enumerate(entries, 1):
        idx      = entry["index"]
        question = entry["question"]
        intent   = entry["intent"]
        candidates = entry["candidates"]

        if idx in done_ids:
            continue

        print(f"  [{i:>4}/{len(entries)}] Q{idx:>4} [{intent:<10}]...",
              end=" ", flush=True)

        # Skip nếu top-1 score quá thấp → retrieval miss
        top1_score = candidates[0]["bge_score"] if candidates else 0
        if top1_score < 0.3:
            out_entry = {
                "index":             idx,
                "question":          question,
                "intent":            intent,
                "gold_indices":      [], # index của chunks đủ để trả lời 
                "partial_indices":   [], # index chunks liên quan nhưng không đủ 
                "irrelevant_indices":[], # index chunks không liên quan 
                "confidence":        "low",
                "expanded":          False,
                "error":             None,
                "status":            "low_score_skip", # low_score_skip nếu top 1 < 0.3
                "top1_bge_score":    round(top1_score, 4),
                "top5_candidates":   [
                    {"rank": c["rank"], "chunk_id": c["chunk_id"],
                     "chunk": c["chunk"], "bge_score": c["bge_score"]}
                    for c in candidates[:TOP_K_JUDGE]
                ],
                "all_candidates_meta": [ # metadata của 20 chunks 
                    {"rank": c["rank"], "chunk_id": c["chunk_id"],
                     "bge_score": c["bge_score"]}
                    for c in candidates
                ],
            }
            out_f.write(json.dumps(out_entry, ensure_ascii=False) + "\n")
            out_f.flush()
            n_none += 1
            print(f"SKIP (top1={top1_score:.3f} < 0.3)")
            continue

        # Lần 1: top-5
        result = call_gpt(client, question, intent, candidates[:TOP_K_JUDGE])
        expanded = False

        # Nếu gold rỗng → expand lên top-10 (chunks 5-9)
        if (not result.get("error") and
                not result.get("gold_indices") and
                len(candidates) > TOP_K_JUDGE):

            result2 = call_gpt(client, question, intent,
                               candidates[TOP_K_JUDGE: TOP_K_JUDGE * 2])

            if result2 and not result2.get("error") and result2.get("gold_indices"):
                # Offset indices về đúng vị trí trong candidates
                result2["gold_indices"]       = [i + TOP_K_JUDGE for i in result2["gold_indices"]]
                result2["partial_indices"]    = [i + TOP_K_JUDGE for i in result2.get("partial_indices", [])]
                result2["irrelevant_indices"] = [i + TOP_K_JUDGE for i in result2.get("irrelevant_indices", [])]
                result  = result2
                expanded = True
                print(f"[expanded] ", end=" ", flush=True)

        if not result:
            result = {"error": "null result"}

        # Build output entry
        out_entry = {
            "index":       idx,
            "question":    question,
            "intent":      intent,
            "gold_indices":         result.get("gold_indices", []),
            "partial_indices":      result.get("partial_indices", []),
            "irrelevant_indices":   result.get("irrelevant_indices", []),
            "confidence":           result.get("confidence", ""),
            "expanded":             expanded,
            "error":                result.get("error", None),
            # Lưu lại top-5 candidates để dùng ở bước sau
            "top5_candidates": [
                {
                    "rank":      c["rank"],
                    "chunk_id":  c["chunk_id"],
                    "chunk":     c["chunk"],
                    "bge_score": c["bge_score"],
                }
                for c in candidates[:TOP_K_JUDGE]
            ],
            # Lưu thêm toàn bộ 20 candidates (chỉ chunk_id + score, không text)
            "all_candidates_meta": [
                {
                    "rank":      c["rank"],
                    "chunk_id":  c["chunk_id"],
                    "bge_score": c["bge_score"],
                }
                for c in candidates
            ],
        }

        out_f.write(json.dumps(out_entry, ensure_ascii=False) + "\n")
        out_f.flush()

        # Stats + log
        has_error = bool(result.get("error"))
        gold      = result.get("gold_indices", [])
        review    = result.get("needs_manual_review", False)

        if has_error:
            n_error += 1
            print(f"ERROR: {result['error'][:50]}")
        elif not gold:
            n_none += 1
            print(f"NONE (conf={result.get('confidence','?')})")
        else:
            n_gold += 1
            print(f"→ gold={gold} conf={result.get('confidence','?')}")

        # ETA
        elapsed = time.time() - t_start
        done_so_far = i - len([x for x in range(i) if entries[x]["index"] in done_ids])
        if done_so_far > 0:
            per_q  = elapsed / done_so_far
            remain = (len(entries) - i) * per_q
            if i % 50 == 0:
                print(f"    ETA: {remain/60:.1f}min | "
                      f"gold={n_gold} none={n_none} "
                      f"error={n_error} review={n_review}")

    out_f.close()

    # Final stats
    print(f"\n{'='*55}")
    print(f"DONE: {args.output}")
    print(f"  Gold found   : {n_gold}")
    print(f"  NONE         : {n_none}")
    print(f"  Errors       : {n_error}")
    print(f"  Need review  : {n_review}")

    # Cost estimate
    n_processed = n_gold + n_none + n_error
    cost = n_processed * TOP_K_JUDGE * 500 / 1e6 * 0.15
    print(f"  Est. API cost: ~${cost:.2f}")

    # Summary stats từ file
    with open(args.output, encoding="utf-8") as f:
        judged = [json.loads(l) for l in f if l.strip()]

    conf_dist = {}
    for e in judged:
        c = e.get("confidence", "unknown")
        conf_dist[c] = conf_dist.get(c, 0) + 1
    print(f"\n  Confidence distribution: {conf_dist}")

    return 0


if __name__ == "__main__":
    exit(main())