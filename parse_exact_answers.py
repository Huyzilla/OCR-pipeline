#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse chính xác đáp án từ QA results JSON
So sánh với ans.md và tạo file kết quả hoàn toàn chính xác
"""

import json
import re
import csv
from pathlib import Path


def load_ground_truth_answers(ans_file):
    """Load đáp án chuẩn từ ans.md"""
    answers = {}
    with open(ans_file, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(',', 1)
            if len(parts) == 2:
                num_choices, choices_str = parts
                choices_str = choices_str.strip('"')
                # Normalize: "A,B,C" -> ["A", "B", "C"]
                choices = sorted([c.strip().upper() for c in choices_str.split(',')])
                answers[idx] = choices
    
    return answers


def parse_llm_answer(answer_text):
    """
    Parse đáp án từ LLM output text
    Handle formats:
    - "B\nGiải thích: ..."
    - "C. Bộ cảm biến thu thập..."
    - "D\n"
    - "Đáp án: A"
    - Multiple: "AB", "ACD", "A,B,C"
    """
    if not answer_text or not isinstance(answer_text, str):
        return []
    
    # Clean text
    text = answer_text.strip().upper()
    
    # Try to find "Đáp án: X" pattern
    match = re.search(r'(?:ĐÁP\s*ÁN|DAP\s*AN)\s*:\s*([A-D,\s]+)', text)
    if match:
        answer_str = match.group(1).strip()
        # Extract letters: "A,B,C" or "A, B, C" or "ABC"
        letters = sorted(list(set(re.findall(r'[A-D]', answer_str))))
        if letters:
            return letters
    
    # Try first line (usually contains the answer)
    first_line = text.split('\n')[0]
    
    # Pattern: "A." or "A\." or "A)"
    match = re.match(r'^([A-D])\s*[\.\)\:]', first_line)
    if match:
        return [match.group(1)]
    
    # Pattern: "A,B,C" or "A B C" or "ABC"
    letters = sorted(list(set(re.findall(r'[A-D]', first_line))))
    if letters and len(letters) <= 4:  # Hợp lý (max 4 choices)
        return letters
    
    # Last resort: tìm letter đầu tiên
    match = re.search(r'[A-D]', text)
    if match:
        return [match.group(1)]
    
    return []


def load_qa_results(json_file):
    """Load QA results from JSON"""
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        if content.endswith(','):
            content = content[:-1]
        if not content.endswith(']'):
            content += ']'
        results = json.loads(content)
    return results


def compare_and_generate_results(qa_results, ground_truth_answers):
    """Compare QA results with ground truth"""
    results = []
    correct_count = 0
    
    for result in qa_results:
        q_idx = result['question_index']
        question = result['question']
        llm_answer_text = result['answer']
        
        # Parse LLM answer
        llm_answer = parse_llm_answer(llm_answer_text)
        
        # Get ground truth
        if q_idx not in ground_truth_answers:
            # Nếu không có GT, skip
            continue
        
        gt_answer = ground_truth_answers[q_idx]
        
        # Compare (chính xác hoàn toàn)
        is_correct = llm_answer == gt_answer
        if is_correct:
            correct_count += 1
        
        results.append({
            'question_index': q_idx,
            'question': question,
            'llm_answer': ','.join(llm_answer) if llm_answer else 'NONE',
            'gt_answer': ','.join(gt_answer) if gt_answer else 'NONE',
            'is_correct': is_correct,
            'llm_raw': llm_answer_text[:200],  # First 200 chars
            'options': result.get('options', []),
            'context_tokens': result.get('context_token_count', 0),
        })
    
    accuracy = 100 * correct_count / len(results) if results else 0
    
    return results, correct_count, accuracy


def save_json_results(results, output_file):
    """Save results to JSON"""
    print(f"Saving JSON results to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved {len(results)} results to {output_file}")


def save_csv_results(results, output_file):
    """Save results to CSV"""
    print(f"Saving CSV results to {output_file}...")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['question_index', 'question', 'llm_answer', 'gt_answer', 'is_correct', 'context_tokens']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow({
                'question_index': result['question_index'],
                'question': result['question'],
                'llm_answer': result['llm_answer'],
                'gt_answer': result['gt_answer'],
                'is_correct': '✓' if result['is_correct'] else '✗',
                'context_tokens': result['context_tokens'],
            })
    print(f"✓ Saved {len(results)} results to {output_file}")


def print_statistics(results, correct_count, accuracy):
    """Print statistics"""
    incorrect_count = len(results) - correct_count
    
    print("\n" + "=" * 80)
    print("📊 EXACT ACCURACY STATISTICS")
    print("=" * 80)
    print(f"\n📈 Total: {len(results)} questions")
    print(f"✅ Correct: {correct_count} ({100*correct_count/len(results):.1f}%)")
    print(f"❌ Incorrect: {incorrect_count} ({100*incorrect_count/len(results):.1f}%)")
    print(f"\n🎯 Exact Accuracy: {accuracy:.1f}%")
    print("=" * 80)
    
    # Show sample incorrect
    incorrect_samples = [r for r in results if not r['is_correct']][:5]
    if incorrect_samples:
        print("\n❌ Sample Incorrect Answers:")
        for item in incorrect_samples:
            print(f"  Q{item['question_index']}: {item['question'][:60]}...")
            print(f"    LLM: {item['llm_answer']} | GT: {item['gt_answer']}")


def export_answer_format(results, output_file):
    """Export kết quả theo format ans.md"""
    print(f"Exporting answer format to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            llm_ans = result['llm_answer']
            # Format: num_choices,answer
            num_choices = len(llm_ans.split(','))
            f.write(f'{num_choices},{llm_ans}\n')
    
    print(f"✓ Exported to {output_file} (format: num_choices,answer)")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Parse QA results with exact accuracy")
    parser.add_argument('--qa-json', type=str, default='qa_results_with_fused_contexts.json',
                       help='QA results JSON file')
    parser.add_argument('--answers', type=str, default='ans.md',
                       help='Ground truth answers file (ans.md)')
    parser.add_argument('--output-json', type=str, default='parsed_qa_results.json',
                       help='Output JSON file')
    parser.add_argument('--output-csv', type=str, default='parsed_qa_results.csv',
                       help='Output CSV file')
    parser.add_argument('--export-answers', type=str, default='llm_answers.txt',
                       help='Export answers in ans.md format')
    
    args = parser.parse_args()
    
    print("🔍 Parsing QA Results with Exact Accuracy\n")
    print("Loading files...")
    
    # Load data
    qa_results = load_qa_results(args.qa_json)
    ground_truth = load_ground_truth_answers(args.answers)
    
    print(f"  ✓ Loaded {len(qa_results)} QA results")
    print(f"  ✓ Loaded {len(ground_truth)} ground truth answers")
    
    # Compare and generate
    print("\n🔄 Parsing answers and comparing...")
    results, correct_count, accuracy = compare_and_generate_results(qa_results, ground_truth)
    
    # Save results
    print("\n💾 Saving results...")
    save_json_results(results, args.output_json)
    save_csv_results(results, args.output_csv)
    export_answer_format(results, args.export_answers)
    
    # Print statistics
    print_statistics(results, correct_count, accuracy)
    
    print(f"\n✅ Done!")
    print(f"   JSON: {args.output_json}")
    print(f"   CSV:  {args.output_csv}")
    print(f"   Answers format: {args.export_answers}\n")


if __name__ == "__main__":
    main()
