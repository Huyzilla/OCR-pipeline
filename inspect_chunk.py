import json
from pathlib import Path

chunk_file = Path('chunk_outputs_finals/Public001/main_chunks_viettel.json')
with open(chunk_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total chunks: {len(data)}')
print(f'Keys in chunk[0]: {list(data[0].keys())}')
total_chars = sum(len(str(d.get("page_content", ""))) for d in data)
print(f'Total chars (all chunks joined): {total_chars}')
print(f'With 6000-char truncate: only {6000/total_chars*100:.1f}% of content is sent')
print()
print('--- Sample chunk[0] page_content (first 300 chars):')
print(str(data[0].get('page_content', ''))[:300])
