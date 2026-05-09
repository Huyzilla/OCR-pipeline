#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C3 Pipeline — Qwen2.5-3B-Instruct + Raw Context
Y HỆT M2 về mọi thứ, chỉ khác: dùng raw context thay vì fused context
"""

import json
import csv
import re
import torch
import time
from pathlib import Path
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────
CHECK_CONTEXTS_FILE = "task2_batch_output_check_contexts.json"
QUESTIONS_CSV_FILE  = "question.csv"
OUTPUT_JSON_FILE    = "c3_qa_results.json"
OUTPUT_CSV_FILE     = "c3_qa_answers.csv"

LLM_MODEL      = "Qwen/Qwen2.5-3B-Instruct"
MAX_NEW_TOKENS = 256
TEMPERATURE    = 0.7   
TOP_P          = 0.9  
DO_SAMPLE      = True


# ── Load data ───────────────────────────────────────────────────────────────
def load_check_contexts(file_path: str) -> dict:
    """Load pre-retrieved contexts, return dict {question_index: context_items}"""
    print(f"Loading contexts from {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    context_map = {}
    for item in data:
        q_idx = item.get("question_index", 0)
        context_map[q_idx] = item.get("context_items", [])

    print(f"Loaded contexts for {len(context_map)} questions")
    return context_map


def load_questions(csv_file: str) -> list:
    """Load questions, 0-indexed để khớp với M2"""
    print(f"Loading questions from {csv_file}...")
    questions = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):  # 0-indexed — y hệt M2
            questions.append({
                "index":    idx,
                "question": row["Question"],
                "options":  [row["A"], row["B"], row["C"], row["D"]],
            })
    print(f"Loaded {len(questions)} questions")
    return questions


# ── Build context ────────────────────────────────────────────────────────────
def build_raw_context(context_items: list, top_k: int = 5) -> str:
    chunks = []
    for item in context_items[:top_k]:
        if isinstance(item, dict):
            chunks.append(item.get("content", ""))
        elif isinstance(item, str):
            chunks.append(item)

    return "\n\n---\n\n".join(c for c in chunks if c)


# ── Prompt — 
def create_prompt(question: str, context: str, options: list) -> str:
    prompt = f"""Dựa vào thông tin sau đây, vui lòng trả lời câu hỏi.

CONTEXT:
{context}

QUESTION:
{question}

OPTIONS:
"""
    for i, opt in enumerate(options):
        prompt += f"{chr(65 + i)}. {opt}\n"

    prompt += "\nANSWER:"
    return prompt


# ── Parse answer — 
def parse_answer(answer_text: str) -> tuple[int, str]:
    if not answer_text or not isinstance(answer_text, str):
        return 0, ""

    # Ưu tiên 1: dòng đầu ngắn có A/B/C/D
    first_line = answer_text.strip().splitlines()[0].strip()
    letters    = re.findall(r"[A-D]", first_line.upper())
    if letters and len(first_line) < 10:
        ordered = list(dict.fromkeys(letters))  # dedup giữ thứ tự
        return len(ordered), ",".join(ordered)

    # Ưu tiên 2: "B. RFID..." pattern
    dot_match = re.match(r"^\s*([A-D])\.", answer_text.strip(), re.IGNORECASE)
    if dot_match:
        return 1, dot_match.group(1).upper()

    # Fallback: 20 ký tự đầu
    early = re.findall(r"[A-D]", answer_text[:20].upper())
    if early:
        return 1, early[0]

    return 0, ""


# ── Model ─────────────────────────────────────────────────────────────────────
def initialize_model(model_name: str):
    print(f"Loading {model_name}...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model     = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map="auto",
        low_cpu_mem_usage=True,
    )
    print("Model loaded")
    return tokenizer, model, device


def generate_answer(tokenizer, model, device, prompt: str) -> tuple[str, float]:
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    t0     = time.time()

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens = MAX_NEW_TOKENS,
            temperature    = TEMPERATURE,
            top_p          = TOP_P,
            do_sample      = DO_SAMPLE,
            pad_token_id   = tokenizer.eos_token_id,
            num_beams      = 1,
            use_cache      = True,
        )

    gen_time = time.time() - t0
    text     = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True
    )
    return text.strip(), gen_time


# ── Main pipeline ─────────────────────────────────────────────────────────────
def run_c3_pipeline(tokenizer, model, device,
                    check_contexts: dict, questions: list,
                    output_json: str, output_csv: str) -> list:

    results = []
    print(f"\nStarting C3 pipeline ({len(questions)} questions)...")
    print("Condition: Raw context + Qwen2.5-3B (same as M2 except context)")
    print("=" * 70)

    with open(output_json, "w", encoding="utf-8") as f:
        f.write("[\n")

    for idx, q_item in enumerate(tqdm(questions, desc="C3")):
        q_idx    = q_item["index"]      # 0-indexed
        question = q_item["question"]
        options  = q_item["options"]

        # Map question_index — dùng q_idx+1 vì context log bắt đầu từ 1
        context_items = check_contexts.get(q_idx + 1, [])
        context       = build_raw_context(context_items, top_k=5)

        if not context:
            context = "Không có ngữ cảnh."

        prompt       = create_prompt(question, context, options)
        answer, gtime = generate_answer(tokenizer, model, device, prompt)
        num, pred    = parse_answer(answer)

        # Format giống M2 output để eval cùng script
        result = {
            "question_index":      q_idx,
            "question":            question,
            "context_token_count": len(context.split()),
            "fusion_time":         0.0,      # không có fusion
            "answer":              answer,
            "parsed_answer":       pred,
            "options":             options,
            "generation_time":     gtime,
            "timestamp":           datetime.now().isoformat(),
        }
        results.append(result)

        with open(output_json, "a", encoding="utf-8") as f:
            if idx > 0:
                f.write(",\n")
            json.dump(result, f, ensure_ascii=False, indent=2)
            f.flush()

        if (idx + 1) % 100 == 0:
            print(f"\n[{idx+1}/{len(questions)}] Q: {question[:50]}...")
            print(f"  Context tokens: {len(context.split())}")
            print(f"  Answer: {pred}")

    with open(output_json, "a", encoding="utf-8") as f:
        f.write("\n]\n")

    # Save CSV — format giống ans.md để eval_accuracy dùng được
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        for r in results:
            pred = r["parsed_answer"]
            if not pred:
                f.write("0,\n")
            elif "," in pred:
                n = len(pred.split(","))
                f.write(f'{n},"{pred}"\n')
            else:
                f.write(f"1,{pred}\n")

    print(f"\n✓ JSON: {output_json}")
    print(f"✓ CSV:  {output_csv}")
    return results


# ── Stats ─────────────────────────────────────────────────────────────────────
def print_stats(results: list) -> None:
    print("\n" + "=" * 70)
    print("C3 STATS — Raw context + Qwen2.5-3B")
    print("=" * 70)

    token_counts = [r["context_token_count"] for r in results]
    gen_times    = [r["generation_time"]     for r in results]
    no_answer    = sum(1 for r in results if not r["parsed_answer"])

    print(f"Total:            {len(results)}")
    print(f"No answer:        {no_answer} ({no_answer/len(results)*100:.1f}%)")
    print(f"Avg ctx tokens:   {sum(token_counts)/len(token_counts):.0f}")
    print(f"Avg gen time:     {sum(gen_times)/len(gen_times):.2f}s")
    print(f"Total time:       {sum(gen_times)/3600:.2f}h")


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    check_contexts = load_check_contexts(CHECK_CONTEXTS_FILE)
    questions      = load_questions(QUESTIONS_CSV_FILE)
    tokenizer, model, device = initialize_model(LLM_MODEL)

    results = run_c3_pipeline(
        tokenizer, model, device,
        check_contexts, questions,
        OUTPUT_JSON_FILE, OUTPUT_CSV_FILE,
    )

    print_stats(results)
    print("\nDone ✓")


if __name__ == "__main__":
    main()