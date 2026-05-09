import json
from pathlib import Path

INPUT = Path('parsed_qa_results.json')
OUTPUT = Path('fusion_answer.md')


def main():
    if not INPUT.exists():
        print(f'Input not found: {INPUT}')
        return
    data = json.loads(INPUT.read_text(encoding='utf-8'))
    lines = []
    for item in data:
        llm = (item.get('llm_answer') or '').strip()
        if not llm or llm.upper() == 'NONE':
            lines.append('0,')
            continue
        # split by comma and normalize
        labels = [s.strip().upper() for s in llm.split(',') if s.strip()]
        labels = [l for l in labels if l in {'A','B','C','D'}]
        if not labels:
            lines.append('0,')
            continue
        count = len(labels)
        if count == 1:
            lines.append(f"{count},{labels[0]}")
        else:
            joined = ",".join(labels)
            lines.append(f"{count},\"{joined}\"")

    OUTPUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Wrote {len(lines)} lines to {OUTPUT}')


if __name__ == '__main__':
    main()
