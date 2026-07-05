import json, csv
from pathlib import Path

PIPELINE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = next((path for path in (PIPELINE_ROOT, *PIPELINE_ROOT.parents) if (path / ".git").exists()), PIPELINE_ROOT)

input_file = PIPELINE_ROOT / "query_gen.jsonl"
output_file = REPO_ROOT / "data" / "question_gen.csv"

rows = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        rows.append({
            "index": obj["index"],
            "question": obj["question"],
            "intent": obj.get("intent", ""),
            "question_gen": obj.get("question_gen", ""),
        })

rows.sort(key=lambda r: r["index"])

with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["index", "question", "intent", "question_gen"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Done: {len(rows)} rows -> {output_file}")
