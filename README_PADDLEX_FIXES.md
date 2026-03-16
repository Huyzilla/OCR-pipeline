# PaddleX Fixes for PaddleOCRVL

File nay ghi lai cac loi da gap va cac chinh sua da thuc hien truc tiep trong moi truong conda `huy` de `PaddleOCRVL` chay duoc.

## 1. Moi truong bi anh huong

- Conda env: `huy`
- Python: `3.11`
- PaddleOCR: `3.4.0`
- PaddleX: `3.4.2`

## 2. Cac loi da gap

### Loi 1: ep `int(...)` truc tiep tu Paddle scalar / tensor

Khi goi `PaddleOCRVL`, PaddleX nem loi:

```text
TypeError: only 0-dimensional arrays can be converted to Python scalars
```

Loi nay xuat hien trong qua trinh xu ly `image_grid_thw` va projector reshape tensor.

### Loi 2: `einops` qua cu khong nhan ra `paddle.Tensor`

Khi goi `PaddleOCRVL`, he thong nem loi:

```text
RuntimeError: Tensor type unknown to einops <class 'paddle.Tensor'>
```

Nguyen nhan la env dang dung `einops==0.2.0`, qua cu so voi stack PaddleOCRVL hien tai.

## 3. Cac file da sua trong thu vien PaddleX

### File 1

File:
- `/media/data3/users/huytq/miniconda3/envs/huy/lib/python3.11/site-packages/paddlex/inference/models/doc_vlm/processors/paddleocr_vl/_paddleocr_vl.py`

Chinh sua:
- Tai doan tao so luong `placeholder` cho image token, khong dung `int(...)` truc tiep nua.
- Thay vao do, neu gia tri co `.item()` thi dung `.item()` roi moi cast sang `int`.

Muc dich:
- Tranh loi khi `image_grid_thw[index].prod()` tra ve Paddle scalar / tensor thay vi Python scalar.

Y tuong patch:

```python
image_count = (
    image_grid_thw[index].prod()
    // self.image_processor.merge_size
    // self.image_processor.merge_size
)
if hasattr(image_count, "item"):
    image_count = int(image_count.item())
else:
    image_count = int(image_count)
```

### File 2

File:
- `/media/data3/users/huytq/miniconda3/envs/huy/lib/python3.11/site-packages/paddlex/inference/models/doc_vlm/modeling/paddleocr_vl/_projector.py`

Chinh sua:
- Them ham `_to_int(...)` de chuyen Paddle scalar sang Python `int` an toan.
- Dung `_to_int(...)` cho `t`, `h`, `w`, `p1`, `p2` truoc khi truyen vao `einops.rearrange(...)`.

Muc dich:
- Tranh loi ep kieu khi Paddle scalar di qua `int(...)` trong projector.

Y tuong patch:

```python
def _to_int(x):
    if hasattr(x, "item"):
        return int(x.item())
    return int(x)
```

Sau do thay:

```python
t=int(t)
h=int(h // m1)
w=int(w // m2)
```

bang:

```python
t=_to_int(t)
h=_to_int(h // m1)
w=_to_int(w // m2)
```

## 4. Package da thay doi trong env

Lenh da chay:

```bash
pip install -U einops
```

Ket qua:
- Nang `einops` tu `0.2.0` len `0.8.2`

Ly do:
- `PaddleOCRVL` can `einops` moi hon de xu ly `paddle.Tensor` dung cach.

Luu y:
- Viec nay co the xung dot version voi `vietocr` neu `vietocr` pin cung `einops==0.2.0`.
- Trong thuc te, pipeline hien tai van chay duoc sau khi nang cap.

## 5. Tai sao phai fix truc tiep trong site-packages

Vi cac loi xay ra ben trong code runtime cua PaddleX, khong nam trong repo lam viec cua ban.
Neu chi sua script ben ngoai thi khong du, vi loi phat sinh trong luc PaddleX / PaddleOCRVL xu ly tensor noi bo.

## 6. Anh huong cua cach fix nay

- Fix nay chi ton tai trong env hien tai: `huy`
- Neu tao env moi, cai lai `paddlex`, hoac update package, cac patch co the bi mat
- Khi do can patch lai

## 7. Cac file pipeline dang phu thuoc vao fix nay

- `/media/data3/users/huytq/huy/ppstructurev3_to_md.py`

Pipeline nay dung:
- `PPStructureV3` de layout analysis
- `VietOCR` cho text recognition o cac vung text
- `PaddleOCRVL` cho table recognition o cac vung bang

Neu bo patch PaddleX thi phan `PaddleOCRVL` co kha nang loi lai.

## 8. Kiem tra nhanh sau khi patch

Co the test bang lenh:

```bash
source /media/data3/users/huytq/miniconda3/etc/profile.d/conda.sh
conda activate huy
export PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True

python /media/data3/users/huytq/huy/ppstructurev3_to_md.py \
  --input /media/data3/users/huytq/huy/Public020.pdf \
  --output_dir /media/data3/users/huytq/huy/outputs_ppstructurev3_md \
  --disable_mkldnn \
  --lang vi \
  --device cpu \
  --vietocr_device cpu \
  --page_header
```

Neu chay thanh cong, file output se nam tai:
- `/media/data3/users/huytq/huy/outputs_ppstructurev3_md/Public020.md`

## 9. Khuyen nghi

Neu ban du dinh dung pipeline nay lau dai, nen lam them 1 script `auto_patch_paddlex.py` hoac 1 patch file de co the ap lai nhanh sau moi lan tao environment moi.
