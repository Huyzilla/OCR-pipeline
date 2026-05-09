#!/usr/bin/env python3
"""
Offline fusion with INCREASED token target (600-800 tokens).
Load pre-retrieved contexts, apply LLM fusion, save fused contexts.
"""

import json
import os
import time
from pathlib import Path
from openai import OpenAI
from tqdm import tqdm

def load_pre_retrieved_contexts(path: Path) -> list:
    """Load pre-retrieved top-5 contexts from task2_batch_output_check_contexts.json."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def fuse_chunks_to_context_v2(client: OpenAI, question: str, chunks: list[str], model: str = "gpt-4o-mini") -> str:
    """
    Fuse multiple chunks into context with HIGHER token target (~600-800).
    """
    if not chunks:
        return ""
    
    try:
        chunks_text = "\n\n---\n\n".join(chunks)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Bạn là chuyên gia tóm tắt và lọc thông tin.\n"
                        "Nhiệm vụ: Đọc câu hỏi và các đoạn văn bản, giữ lại thông tin liên quan đến câu hỏi.\n"
                        "- Giữ ngôn cảnh đủ để trả lời câu hỏi\n"
                        "- Loại bỏ thông tin trùng lặp\n"
                        "- Giữ các định nghĩa, con số, ví dụ quan trọng\n"
                        "- Tổng length: ~600-800 tokens (khoảng 400-600 từ)\n"
                        "- Trả về văn bản dễ đọc"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"[CÂU HỎI]\n{question}\n\n"
                        f"[CÁC ĐOẠN VĂNBẢN]\n{chunks_text}\n\n"
                        f"Hãy lọc và tóm tắt chỉ giữ thông tin cần thiết cho câu hỏi trên."
                    ),
                },
            ],
            temperature=0.1,
        )
        fused = response.choices[0].message.content or ""
        return fused.strip() if fused else "\n\n".join(chunks)
    except Exception as e:
        print(f"Warning: Fusion LLM call failed ({e}), falling back to raw chunks")
        return "\n\n".join(chunks)

def estimate_token_count(text: str) -> int:
    """Estimate token count (1 token ≈ 0.75 words)."""
    words = len(text.split())
    return int(words / 0.75)

def main():
    print("Loading pre-retrieved contexts...")
    pre_retrieved = load_pre_retrieved_contexts(Path("task2_batch_output_check_contexts.json"))
    print(f"  Loaded {len(pre_retrieved)} pre-retrieved context entries")
    
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    fused_contexts = []
    
    print("\nApplying fusion with increased token target (600-800 tokens)...")
    start_time = time.time()
    
    for idx in tqdm(range(len(pre_retrieved)), desc="Fusing"):
        entry = pre_retrieved[idx]
        question = entry.get("question", "")
        
        # Extract chunks from context_items
        context_items = entry.get("context_items", [])
        chunks = [item.get("content", "") for item in context_items if item.get("content", "").strip()]
        
        fusion_start = time.time()
        fused_context = fuse_chunks_to_context_v2(client, question, chunks)
        fusion_time = time.time() - fusion_start
        
        token_count = estimate_token_count(fused_context)
        
        fused_contexts.append({
            "question_index": idx,
            "question": question,
            "llm_context": fused_context,
            "fusion_time": fusion_time,
            "context_token_count": token_count,
        })
    
    total_time = time.time() - start_time
    
    # Save fused contexts
    output_path = Path("task2_batch_output_fused_contexts_v2.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(fused_contexts, f, ensure_ascii=False, indent=2)
    
    # Compute stats
    token_counts = [f["context_token_count"] for f in fused_contexts]
    avg_tokens = sum(token_counts) / len(token_counts) if token_counts else 0
    
    print(f"\n{'='*80}")
    print(f"FUSION COMPLETE (V2 - Increased Token Target)")
    print(f"{'='*80}")
    print(f"Processed: {len(fused_contexts)}/991 questions")
    print(f"Total time: {total_time/60:.1f} minutes ({total_time/3600:.2f} hours)")
    print(f"Average time per question: {total_time/len(fused_contexts):.2f}s")
    print(f"\nContext token statistics:")
    print(f"  Average: {avg_tokens:.0f} tokens")
    print(f"  Min: {min(token_counts)} tokens")
    print(f"  Max: {max(token_counts)} tokens")
    print(f"  Stdev: {(sum((x - avg_tokens)**2 for x in token_counts) / len(token_counts))**0.5:.0f} tokens")
    print(f"\nSaved to {output_path}")

if __name__ == "__main__":
    main()
