import csv
import re

def extract_choices(text):
    text = text.strip()
    if not text:
        return []
    
    # Try finding A, B, C, D in the text if it starts with A.
    match = re.match(r'^([A-D])\.', text, re.IGNORECASE)
    if match:
        return [match.group(1).upper()]
        
    # Check for 'ANSWER: A' or 'A, B' at the beginning
    match = re.search(r'^(?:ANSWER:\s*)?([A-D](?:\s*,\s*[A-D])*)\b', text, re.IGNORECASE)
    if match:
        choices = [c.strip().upper() for c in match.group(1).split(',')]
        return choices
        
    return []

truths = []
with open('ans.md', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        parts = line.split(',', 1)
        if len(parts) == 2:
            truth_ans = [c.strip().upper() for c in parts[1].replace('\"', '').split(',')]
            truths.append(truth_ans)

preds = []
with open('output_pipeline.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 2:
            preds.append(extract_choices(row[1]))

correct = 0
total = min(len(truths), len(preds))
for i in range(total):
    t = set(truths[i])
    p = set(preds[i])
    if t == p and len(t) > 0:
        correct += 1
    # else:
    #     print(f"Mismatch at {i+1}: Truth={t}, Pred={p} (Raw: {preds[i]})")

print(f'Total questions evaluated: {total}')
print(f'Correct: {correct}')
print(f'Accuracy: {correct/total*100:.2f}%')
