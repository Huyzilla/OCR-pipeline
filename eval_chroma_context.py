import pandas as pd
import json
from statistics import mean, median

# Load GT chunks (index_question 200-299)
df_gt = pd.read_csv("chunk_context_200_299.csv")

# Load pre-retrieved chunks from task2_batch_output_check_contexts.json
with open("task2_batch_output_check_contexts.json", "r", encoding="utf-8") as f:
    pre_retrieved = json.load(f)

# Create dict mapping question_index -> context_items
retrieved_by_index = {item["question_index"]: item["context_items"] for item in pre_retrieved}

print(f"Loaded {len(df_gt)} GT chunks")
print(f"Loaded {len(pre_retrieved)} pre-retrieved chunks")
print(f"Retrieved dict size: {len(retrieved_by_index)}\n")

def chunk_coverage_score(gt_chunk: str, retrieved_chunk: str) -> float:
    """% GT tokens được cover bởi retrieved chunk"""
    gt_tokens  = set(gt_chunk.lower().split())
    ret_tokens = set(retrieved_chunk.lower().split())
    
    if not gt_tokens:
        return 0.0
    
    overlap = len(gt_tokens & ret_tokens)
    return overlap / len(gt_tokens)

def find_best_coverage_in_top_k(gt_chunk: str, retrieved_chunks: list) -> tuple:
    """Tìm chunk có coverage cao nhất. Returns: (rank, best_coverage, all_coverages)"""
    if not retrieved_chunks:
        return None, 0.0, []
    
    coverages = [chunk_coverage_score(gt_chunk, chunk) for chunk in retrieved_chunks]
    best_idx = max(range(len(coverages)), key=lambda i: coverages[i])
    
    return best_idx + 1, coverages[best_idx], coverages

def merged_coverage_score(gt_chunk: str, retrieved_chunks: list) -> float:
    """% GT tokens được cover bởi merged top-k chunks"""
    gt_tokens = set(gt_chunk.lower().split())
    
    if not gt_tokens:
        return 0.0
    
    merged_text = " ".join(retrieved_chunks)
    merged_tokens = set(merged_text.lower().split())
    
    overlap = len(gt_tokens & merged_tokens)
    return overlap / len(gt_tokens)

def eval_recall_from_precomputed(limit: int = None) -> dict:
    """
    Đo coverage dựa vào pre-retrieved chunks từ task2_batch_output_check_contexts.json
    """
    single_chunk_hits = []
    merged_hits_30 = []
    merged_hits_50 = []
    merged_hits_70 = []
    
    all_single_coverages = []
    all_merged_coverages = []
    
    debug_log = []
    
    test_df = df_gt.head(limit) if limit else df_gt

    for idx, (_, gt_row) in enumerate(test_df.iterrows()):
        q_idx = gt_row["index_question"]  # Already correctly mapped
        gt_chunk = gt_row["chunk_context"].strip()
        
        # Lấy pre-retrieved chunks
        if q_idx not in retrieved_by_index:
            print(f"[SKIP] Q{q_idx} not in pre-retrieved dict")
            continue
        
        context_items = retrieved_by_index[q_idx]
        top_5_docs = [item["content"] for item in context_items[:5]]
        
        # Metric 1: Best single chunk
        best_rank, best_coverage, single_coverages = find_best_coverage_in_top_k(gt_chunk, top_5_docs)
        all_single_coverages.append(best_coverage)
        
        if best_coverage >= 0.4:
            single_chunk_hits.append((q_idx, best_rank, best_coverage))
        
        # Metric 2: Merged coverage
        merged_cov = merged_coverage_score(gt_chunk, top_5_docs)
        all_merged_coverages.append(merged_cov)
        
        if merged_cov >= 0.3:
            merged_hits_30.append((q_idx, merged_cov))
        if merged_cov >= 0.5:
            merged_hits_50.append((q_idx, merged_cov))
        if merged_cov >= 0.7:
            merged_hits_70.append((q_idx, merged_cov))
        
        # Debug log
        debug_log.append({
            "q_idx": q_idx,
            "gt_length_words": len(gt_chunk.split()),
            "best_single_coverage": float(best_coverage),
            "best_single_rank": best_rank,
            "merged_coverage": float(merged_cov),
            "top_5_chunks": top_5_docs,
            "single_coverages": [float(s) for s in single_coverages],
        })
        
        # In chi tiết
        print(f"[Q{q_idx}] GT: {len(gt_chunk.split())} words")
        print(f"  Single: Rank {best_rank}, Coverage {best_coverage:.1%}")
        print(f"  Merged coverage: {merged_cov:.1%}")

    total = len(test_df)

    return {
        "summary": {
            "total_questions": total,
            "single_chunk_avg": mean(all_single_coverages) if all_single_coverages else 0,
            "single_chunk_median": median(all_single_coverages) if all_single_coverages else 0,
            "merged_coverage_avg": mean(all_merged_coverages) if all_merged_coverages else 0,
            "merged_coverage_median": median(all_merged_coverages) if all_merged_coverages else 0,
        },
        "single_chunk_hits_40": {
            "hits": len(single_chunk_hits),
            "recall_percent": 100 * len(single_chunk_hits) / total if total > 0 else 0,
        },
        "merged_coverage_30": {
            "hits": len(merged_hits_30),
            "recall_percent": 100 * len(merged_hits_30) / total if total > 0 else 0,
        },
        "merged_coverage_50": {
            "hits": len(merged_hits_50),
            "recall_percent": 100 * len(merged_hits_50) / total if total > 0 else 0,
        },
        "merged_coverage_70": {
            "hits": len(merged_hits_70),
            "recall_percent": 100 * len(merged_hits_70) / total if total > 0 else 0,
        },
        "debug_log": debug_log,
    }

# Run on all 100 questions
print("=" * 70)
print("RECALL — Pre-retrieved chunks (100 câu)")
print("=" * 70)

r = eval_recall_from_precomputed(limit=None)

print("\n" + "=" * 70)
print("RESULTS (Stats)")
print("=" * 70)
print(f"Total questions: {r['summary']['total_questions']}")
print(f"\nSingle chunk best coverage:")
print(f"  Avg: {r['summary']['single_chunk_avg']:.1%}")
print(f"  Median: {r['summary']['single_chunk_median']:.1%}")
print(f"\nMerged coverage:")
print(f"  Avg: {r['summary']['merged_coverage_avg']:.1%}")
print(f"  Median: {r['summary']['merged_coverage_median']:.1%}")

print(f"\n" + "=" * 70)
print("RESULTS (Thresholds)")
print("=" * 70)
print(f"\n1. Best single chunk (coverage >= 40%):")
print(f"   Recall: {r['single_chunk_hits_40']['recall_percent']:.1f}% ({r['single_chunk_hits_40']['hits']}/{r['summary']['total_questions']})")

print(f"\n2. Merged top-5 (coverage >= 30%):")
print(f"   Recall: {r['merged_coverage_30']['recall_percent']:.1f}% ({r['merged_coverage_30']['hits']}/{r['summary']['total_questions']})")

print(f"\n3. Merged top-5 (coverage >= 50%):")
print(f"   Recall: {r['merged_coverage_50']['recall_percent']:.1f}% ({r['merged_coverage_50']['hits']}/{r['summary']['total_questions']})")

print(f"\n4. Merged top-5 (coverage >= 70%):")
print(f"   Recall: {r['merged_coverage_70']['recall_percent']:.1f}% ({r['merged_coverage_70']['hits']}/{r['summary']['total_questions']})")

# Save detailed JSON
detailed_results = {
    "summary": r["summary"],
    "threshold_results": {
        "single_chunk_40": r["single_chunk_hits_40"],
        "merged_30": r["merged_coverage_30"],
        "merged_50": r["merged_coverage_50"],
        "merged_70": r["merged_coverage_70"],
    },
    "per_question": r["debug_log"],
}

with open("eval_recall_debug.json", "w", encoding="utf-8") as f:
    json.dump(detailed_results, f, ensure_ascii=False, indent=2)
print("\n[OK] Detailed results saved to: eval_recall_debug.json")
