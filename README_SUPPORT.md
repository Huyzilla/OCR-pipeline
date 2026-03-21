# Huong dan chay PaddleOCR cho Public020.pdf

## 1) Kich hoat dung moi truong conda

```bash
source /media/data3/users/huytq/miniconda3/etc/profile.d/conda.sh
conda activate huy
```

## 2) Chay PaddleOCR KHONG CAN viet code (CLI)

Co. PaddleOCR chay duoc bang lenh CLI, khong bat buoc viet file Python.

Lenh uu tien cho tai lieu tieng Viet:

```bash
paddleocr ocr \
  -i /media/data3/users/huytq/huy/Public020.pdf \
  --save_path /media/data3/users/huytq/huy/output_public020_vi \
  --lang vi \
  --device cpu \
  --enable_mkldnn False \
  --enable_cinn False
```

Lenh ben duoi la ban da dung truoc do (lang mac dinh):

```bash
paddleocr ocr \
  -i /media/data3/users/huytq/huy/Public020.pdf \
  --save_path /media/data3/users/huytq/huy/output_public020 \
  --device cpu \
  --enable_mkldnn False \
  --enable_cinn False
```

Ghi chu:
- `--enable_mkldnn False` de tranh loi oneDNN/PIR tren may CPU (loi ban gap truoc do).
- Ket qua se duoc ghi vao thu muc `output_public020`.
- OCR tieng Viet da test lai va luu thanh file `Public020_paddleocr_vi.txt`.

## 3) Neu muon xuat text thuong (.txt)

Ban da co file OCR text mau tai:
- `/media/data3/users/huytq/huy/Public020_paddleocr.txt`
- `/media/data3/users/huytq/huy/Public020_paddleocr_vi.txt`

Neu can chay lai theo Python (de chu dong format output), dung doan lenh sau:

```bash
python - <<'PY'
from pathlib import Path
from paddleocr import PaddleOCR

pdf_path = Path('/media/data3/users/huytq/huy/Public020.pdf')
out_path = Path('/media/data3/users/huytq/huy/Public020_paddleocr.txt')

ocr = PaddleOCR(lang='en', device='cpu', enable_mkldnn=False, enable_cinn=False)
res = ocr.predict(str(pdf_path))

lines = []
for page_idx, page in enumerate(res, 1):
    lines.append(f'=== PAGE {page_idx} ===')
    rec_texts = page.get('rec_texts') if isinstance(page, dict) else getattr(page, 'rec_texts', None)
    if rec_texts:
        lines.extend([str(t) for t in rec_texts if t])
    lines.append('')

out_path.write_text('\n'.join(lines), encoding='utf-8')
print('Saved:', out_path)
PY
```

## 4) Kiem tra nhanh

```bash
wc -l /media/data3/users/huytq/huy/Public020_paddleocr.txt
head -n 30 /media/data3/users/huytq/huy/Public020_paddleocr.txt
```

## 5) Pipeline lai: Paddle detect + VietOCR recognize

Ban da co script san:
- `/media/data3/users/huytq/huy/paddle_det_vietocr.py`

Chay pipeline:

```bash
python /media/data3/users/huytq/huy/paddle_det_vietocr.py \
  --input /media/data3/users/huytq/huy/Public020.pdf \
  --output_txt /media/data3/users/huytq/huy/Public020_paddle_det_vietocr.txt \
  --disable_mkldnn \
  --vietocr_device cpu
```

Output:
- TXT: `/media/data3/users/huytq/huy/Public020_paddle_det_vietocr.txt`
- JSON (kem box): `/media/data3/users/huytq/huy/Public020_paddle_det_vietocr.json`

Ghi chu:
- Pipeline nay dung PaddleOCR de tim box text, sau do dung VietOCR local trong folder `vietocr/` de nhan dien text.
- Da sua tuong thich Pillow moi trong `vietocr/tool/translate.py`.

## 6) Pipeline theo layout: PPStructureV3 + OCR theo tung vung + xuat .md

Script:
- `/media/data3/users/huytq/huy/ppstructurev3_to_md.py`

Y tuong:
- PPStructureV3: layout analysis (tach block va sap xep theo thu tu doc)
- Vung text: PaddleOCR -> text
- Vung table: PaddleOCRVL -> table (HTML), sau do doi sang Markdown table
- Ghep ket qua theo thu tu tren-xuong duoi -> file `.md`

Chay cho 1 file:

```bash
python /media/data3/users/huytq/huy/ppstructurev3_to_md.py \
  --input /media/data3/users/huytq/huy/Public283.pdf \
  --output_dir /media/data3/users/huytq/huy/outputs_ppstructurev3_md \
  --lang vi \
  --device cpu \
  --disable_mkldnn \
  --page_header
```

Chay cho nhieu file PDF trong folder data:

```bash
python /media/data3/users/huytq/huy/ppstructurev3_to_md.py \
  --input /media/data3/users/huytq/huy/data \
  --output_dir /media/data3/users/huytq/huy/outputs_ppstructurev3_md \
  --lang vi \
  --device cpu \
  --disable_mkldnn \
  --page_header
```

Output mau:
- `/media/data3/users/huytq/huy/outputs_ppstructurev3_md/Public020.md`

