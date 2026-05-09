#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để chạy QA với fused contexts
Sử dụng:
  - Embedding model: AITeamVN/Vietnamese_Embedding_v2
  - LLM: Qwen/Qwen2.5-3B-Instruct
"""

import json
import csv
import torch
import argparse
from pathlib import Path
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM
from datetime import datetime

# Cấu hình
FUSED_CONTEXTS_FILE = "task2_batch_output_fused_contexts_v2.json"
QUESTIONS_CSV_FILE = "question.csv"
OUTPUT_FILE = "qa_results_with_fused_contexts.json"
OUTPUT_CSV_FILE = "qa_results_with_fused_contexts.csv"

# LLM config
LLM_MODEL = "Qwen/Qwen2.5-3B-Instruct"
MAX_NEW_TOKENS = 256
TEMPERATURE = 0.7
TOP_P = 0.9


def load_fused_contexts(file_path):
    """Load fused contexts từ JSON file"""
    print(f"Loading fused contexts from {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} fused contexts")
    return data


def load_questions(csv_file):
    """Load questions từ CSV file"""
    print(f"Loading questions from {csv_file}...")
    questions = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            questions.append({
                'index': idx,
                'question': row['Question'],
                'options': [row['A'], row['B'], row['C'], row['D']]
            })
    print(f"Loaded {len(questions)} questions")
    return questions


def create_prompt(question, context, options=None):
    """Tạo prompt cho LLM"""
    prompt = f"""Dựa vào thông tin sau đây, vui lòng trả lời câu hỏi.

CONTEXT:
{context}

QUESTION:
{question}
"""
    
    if options:
        prompt += "\nOPTIONS:\n"
        for i, opt in enumerate(options):
            prompt += f"{chr(65 + i)}. {opt}\n"
    
    prompt += "\nANSWER:"
    return prompt


def initialize_model(model_name):
    """Khởi tạo LLM model"""
    print(f"Loading LLM model: {model_name}...")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map="auto"
    )
    
    print(f"Model loaded successfully")
    return tokenizer, model, device


def generate_answer(tokenizer, model, device, prompt, max_tokens=MAX_NEW_TOKENS):
    """Generate answer từ LLM"""
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Decode chỉ phần generated (không include input)
    generated_text = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    return generated_text.strip()


def run_qa_pipeline(tokenizer, model, device, fused_contexts, questions, output_json_file, output_csv_file):
    """Chạy QA pipeline - ghi incremental real-time"""
    results = []
    
    print(f"\nStarting QA pipeline with {len(questions)} questions...")
    print(f"Output will be saved to: {output_json_file}")
    print("=" * 80)
    
    # Mở file JSON để append
    with open(output_json_file, 'w', encoding='utf-8') as f:
        f.write("[\n")
    
    for idx, fused_ctx in enumerate(tqdm(fused_contexts, desc="Processing questions")):
        q_idx = fused_ctx['question_index']
        question = fused_ctx['question']
        context = fused_ctx['llm_context']
        
        # Lấy options từ questions
        options = questions[q_idx]['options'] if q_idx < len(questions) else None
        
        # Tạo prompt
        prompt = create_prompt(question, context, options)
        
        # Generate answer
        answer = generate_answer(tokenizer, model, device, prompt)
        
        # Lưu kết quả
        result = {
            'question_index': q_idx,
            'question': question,
            'context_token_count': fused_ctx['context_token_count'],
            'fusion_time': fused_ctx['fusion_time'],
            'answer': answer,
            'options': options,
            'timestamp': datetime.now().isoformat()
        }
        
        results.append(result)
        
        # Ghi incremental vào JSON file
        with open(output_json_file, 'a', encoding='utf-8') as f:
            if idx > 0:
                f.write(",\n")
            json.dump(result, f, ensure_ascii=False, indent=2)
            f.flush()  # Flush để ghi ngay lập tức
        
        # In log mỗi 50 questions
        if (q_idx + 1) % 50 == 0:
            print(f"\n✓ Processed {q_idx + 1}/{len(fused_contexts)} questions")
            print(f"  Q: {question[:50]}...")
            print(f"  A: {answer[:70]}...")
    
    # Đóng JSON array
    with open(output_json_file, 'a', encoding='utf-8') as f:
        f.write("\n]\n")
    
    return results


def save_results(results, json_file, csv_file):
    """Lưu kết quả (JSON đã ghi incremental, chỉ cần CSV)"""
    print(f"\nFinalizing results...")
    
    # JSON đã ghi xong (incremental), chỉ validate
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            saved_results = json.load(f)
        print(f"✓ JSON file verified: {len(saved_results)} results")
    except Exception as e:
        print(f"⚠ Warning reading JSON: {e}")
        saved_results = results
    
    # Save as CSV
    print(f"Saving results to {csv_file}...")
    if results:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['question_index', 'question', 'answer', 'context_token_count', 
                         'fusion_time', 'option_A', 'option_B', 'option_C', 'option_D', 'timestamp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                row = {
                    'question_index': result['question_index'],
                    'question': result['question'],
                    'answer': result['answer'],
                    'context_token_count': result['context_token_count'],
                    'fusion_time': result['fusion_time'],
                    'timestamp': result.get('timestamp', ''),
                }
                if result['options']:
                    row['option_A'] = result['options'][0]
                    row['option_B'] = result['options'][1]
                    row['option_C'] = result['options'][2]
                    row['option_D'] = result['options'][3]
                
                writer.writerow(row)
    
    print(f"✓ CSV file saved: {csv_file}")
    
    # Print statistics
    print("\n" + "=" * 80)
    print(f"✅ COMPLETED: {len(results)} questions")
    if results:
        print(f"Avg context tokens: {sum(r['context_token_count'] for r in results) / len(results):.2f}")
        print(f"Avg fusion time: {sum(r['fusion_time'] for r in results) / len(results):.2f}s")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Run QA with fused contexts")
    parser.add_argument('--model', type=str, default=LLM_MODEL, help='LLM model name')
    parser.add_argument('--fused-contexts', type=str, default=FUSED_CONTEXTS_FILE, 
                       help='Path to fused contexts JSON file')
    parser.add_argument('--questions', type=str, default=QUESTIONS_CSV_FILE, 
                       help='Path to questions CSV file')
    parser.add_argument('--output-json', type=str, default=OUTPUT_FILE, 
                       help='Output JSON file path')
    parser.add_argument('--output-csv', type=str, default=OUTPUT_CSV_FILE, 
                       help='Output CSV file path')
    parser.add_argument('--max-tokens', type=int, default=MAX_NEW_TOKENS, 
                       help='Max tokens for generation')
    args = parser.parse_args()
    
    # Load data
    fused_contexts = load_fused_contexts(args.fused_contexts)
    questions = load_questions(args.questions)
    
    # Initialize model
    tokenizer, model, device = initialize_model(args.model)
    
    # Run pipeline
    results = run_qa_pipeline(tokenizer, model, device, fused_contexts, questions, args.output_json, args.output_csv)
    
    # Save CSV (từ results)
    save_results(results, args.output_json, args.output_csv)
    
    print("\nDone! ✓")


if __name__ == "__main__":
    main()
