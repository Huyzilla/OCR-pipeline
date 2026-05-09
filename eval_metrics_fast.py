"""
Fast evaluation metrics from baseline results (no tokenizer overhead):
1. Avg Context Tokens (word-based approximation: words / 0.75)
2. Context size distribution
3. Retrieved documents per question
"""
import json
from pathlib import Path
from typing import Any
import statistics


def approximate_tokens(text: str) -> int:
    """
    Approximate token count without loading a tokenizer model.
    Rule of thumb: 1 token ≈ 0.75 words
    """
    words = len(text.split())
    return max(1, int(words / 0.75))


def compute_metrics(contexts_file: Path) -> dict[str, Any]:
    """Parse contexts JSON and compute metrics."""
    with open(contexts_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        return {"error": "Unexpected JSON format"}
    
    llm_context_tokens = []
    item_tokens_all = []
    items_per_question = []
    
    for item in data:
        if not isinstance(item, dict):
            continue
        
        # Full LLM context
        llm_context = item.get("llm_context", "")
        if llm_context:
            tokens = approximate_tokens(llm_context)
            llm_context_tokens.append(tokens)
        
        # Individual context items
        context_items = item.get("context_items", [])
        num_items = len(context_items)
        items_per_question.append(num_items)
        
        for ctx in context_items:
            if isinstance(ctx, dict):
                content = ctx.get("content", "")
                if content:
                    tokens = approximate_tokens(content)
                    item_tokens_all.append(tokens)
    
    if not llm_context_tokens:
        return {"error": "No context data found"}
    
    # Statistics
    return {
        "total_questions": len(llm_context_tokens),
        "llm_context_tokens": {
            "mean": round(statistics.mean(llm_context_tokens), 0),
            "median": round(statistics.median(llm_context_tokens), 0),
            "min": min(llm_context_tokens),
            "max": max(llm_context_tokens),
            "stdev": round(statistics.stdev(llm_context_tokens), 0) if len(llm_context_tokens) > 1 else 0,
        },
        "item_tokens": {
            "total_items": len(item_tokens_all),
            "mean_per_item": round(statistics.mean(item_tokens_all), 0) if item_tokens_all else 0,
            "median_per_item": round(statistics.median(item_tokens_all), 0) if item_tokens_all else 0,
        },
        "items_per_question": {
            "mean": round(statistics.mean(items_per_question), 1),
            "median": statistics.median(items_per_question),
            "min": min(items_per_question),
            "max": max(items_per_question),
        }
    }


def main():
    contexts_file = Path("task2_batch_output_check_contexts.json")
    
    if not contexts_file.exists():
        print(f"❌ Contexts file not found: {contexts_file}")
        return
    
    print("=" * 75)
    print("BASELINE EVALUATION METRICS")
    print("=" * 75)
    
    metrics = compute_metrics(contexts_file)
    
    if "error" in metrics:
        print(f"⚠️  {metrics['error']}")
        return
    
    print(f"\n📊 CONTEXT TOKEN ANALYSIS")
    print("-" * 75)
    print(f"Questions processed: {metrics['total_questions']}")
    print(f"\nFull LLM Context (all 5 chunks concatenated per question):")
    ctx_tokens = metrics['llm_context_tokens']
    print(f"  Average tokens: {ctx_tokens['mean']:.0f}")
    print(f"  Median tokens:  {ctx_tokens['median']:.0f}")
    print(f"  Std. Dev:       {ctx_tokens['stdev']:.0f}")
    print(f"  Range:          {ctx_tokens['min']} - {ctx_tokens['max']}")
    
    print(f"\nIndividual Context Items:")
    item_tokens = metrics['item_tokens']
    print(f"  Total chunks retrieved: {item_tokens['total_items']}")
    print(f"  Avg tokens per chunk:   {item_tokens['mean_per_item']:.0f}")
    print(f"  Median tokens:          {item_tokens['median_per_item']:.0f}")
    
    print(f"\nChunks per Question (context_items):")
    items = metrics['items_per_question']
    print(f"  Average:  {items['mean']:.1f} chunks")
    print(f"  Median:   {items['median']} chunks")
    print(f"  Range:    {items['min']} - {items['max']} chunks")
    
    print("\n" + "=" * 75)
    print("NOTE: Token counts are approximate (words / 0.75)")
    print("      For exact counts, use a proper tokenizer")
    print("=" * 75)


if __name__ == "__main__":
    main()
