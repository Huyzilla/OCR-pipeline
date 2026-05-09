#!/usr/bin/env python3
"""
Classify 991 queries into two categories (tra_cuu or tinh_toan) using Qwen2.5 1.5B Instruct
"""

import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm
from datetime import datetime
import os

# Configuration
MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
INPUT_FILE = "question.csv"
OUTPUT_FILE = "qwen_intent_classification.csv"

# CPU optimization
DEVICE = "cpu"
torch.set_num_threads(os.cpu_count())

# System prompt for classification
SYSTEM_PROMPT = """Bạn là một chuyên gia phân loại câu hỏi tiếng Việt. 
Phân loại câu hỏi sau vào một trong hai loại:
- tra_cuu: Câu hỏi yêu cầu tìm kiếm, tra cứu thông tin từ tài liệu
- tinh_toan: Câu hỏi yêu cầu tính toán, suy luận, xử lý thông tin

Chỉ trả lời bằng một trong hai từ: "tra_cuu" hoặc "tinh_toan". KHÔNG giải thích thêm."""

def load_questions():
    """Load questions from CSV file"""
    print(f"Loading questions from {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    questions = df['Question'].tolist()
    print(f"Loaded {len(questions)} questions")
    return questions


def save_progress(results):
    """Write current progress to disk so the file exists while the run is still active."""
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

def classify_questions(questions):
    """Classify questions using Qwen2.5 1.5B Instruct (CPU optimized)"""
    print(f"\nInitializing Qwen2.5 1.5B Instruct on CPU (int8 quantization)...")
    
    try:
        # Load with int8 quantization for CPU
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
        
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            load_in_8bit=False,  # int8 on CPU with bitsandbytes sometimes has issues
            torch_dtype=torch.float32,
            device_map="cpu",
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        
        # Move to CPU and set to eval mode
        model = model.to(DEVICE)
        model.eval()
        
        print(f"Model loaded successfully on CPU\n")
        
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Falling back to pipeline initialization...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float32,
            device_map="cpu",
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        model = model.to(DEVICE)
        model.eval()
    
    print(f"Classifying {len(questions)} questions on CPU...")
    
    results = []
    errors = []

    # Create the output file immediately so progress can be checked while running.
    save_progress(results)
    
    for i, question in enumerate(tqdm(questions, desc="Classifying")):
        try:
            # Build the message for the model
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Câu hỏi: {question}"}
            ]
            
            # Tokenize
            text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(text, return_tensors="pt").to(DEVICE)
            
            # Generate with optimized settings for CPU
            with torch.no_grad():
                output_ids = model.generate(
                    **inputs,
                    max_new_tokens=20,
                    do_sample=False,
                    temperature=1.0,
                    num_beams=1,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            # Decode response
            response_ids = output_ids[0][inputs["input_ids"].shape[-1]:]
            response = tokenizer.decode(response_ids, skip_special_tokens=True).strip().lower()
            
            # Validate and normalize the response
            if "tra_cuu" in response:
                intent = "tra_cuu"
            elif "tinh_toan" in response:
                intent = "tinh_toan"
            else:
                # Fallback: try to extract the main classification word
                if "tra" in response:
                    intent = "tra_cuu"
                elif "tinh" in response:
                    intent = "tinh_toan"
                else:
                    intent = "tra_cuu"  # Default fallback
            
            results.append({
                "question_index": i,
                "question": question,
                "intent": intent
            })

            save_progress(results)
            
            # Clear cache
            torch.cuda.empty_cache()
            
        except Exception as e:
            error_msg = f"Q{i}: {str(e)}"
            errors.append(error_msg)
            results.append({
                "question_index": i,
                "question": question,
                "intent": "tra_cuu"  # Default on error
            })

            save_progress(results)
    
    if errors:
        print(f"\n⚠️  {len(errors)} errors encountered during classification")
    
    return results

def save_results(results):
    """Save results to CSV file"""
    print(f"\nSaving results to {OUTPUT_FILE}...")
    
    # Final write of the full results with questions
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    
    # Print statistics
    print(f"✅ Results saved to {OUTPUT_FILE}")
    
    # Print statistics
    intent_counts = df['intent'].value_counts()
    print(f"\nClassification Summary:")
    print(f"  - tra_cuu: {intent_counts.get('tra_cuu', 0)} questions")
    print(f"  - tinh_toan: {intent_counts.get('tinh_toan', 0)} questions")
    print(f"  - Total: {len(df)} questions")

def main():
    """Main execution"""
    print("=" * 60)
    print("Qwen2.5 1.5B Intent Classification")
    print("=" * 60)
    print(f"Start time: {datetime.now()}\n")
    
    # Load questions
    questions = load_questions()
    
    # Classify
    results = classify_questions(questions)
    
    # Save results
    save_results(results)
    
    print(f"\nEnd time: {datetime.now()}")
    print("=" * 60)

if __name__ == "__main__":
    main()
