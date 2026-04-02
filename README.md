# OCR Pipeline

Pipeline chuẩn để chạy dữ liệu PDF trong dự án này là:

1. Crop header trước bằng `crop_header.py`
2. OCR sau bằng `ocr.py`

## 1) Chuẩn bị môi trường

Luôn kích hoạt môi trường `huy` trước khi chạy bất kỳ script nào:

```powershell
conda activate your_env
```

Cài thư viện:

```powershell
pip install -r requirements.txt
```

## 2) Bước 1 - Crop header

### Chạy cho cả thư mục

```powershell
python crop_header.py --input_dir input --output_dir cropped_pdfs
```

Kết quả mặc định sẽ tạo file dạng `*_cropped.pdf` trong thư mục `cropped_pdfs`.

### Chạy cho 1 file

```powershell
python crop_header.py --input_pdf input/Public283.pdf --output_pdf cropped_pdfs/Public283_cropped.pdf
```

## 3) Bước 2 - OCR (sau khi crop)

### Chạy cho cả thư mục cropped

```powershell
python ocr.py --input_dir cropped_pdfs --output_dir outputs --table_format html
```

### Chạy cho 1 file cropped

```powershell
python ocr.py --input_pdf cropped_pdfs/Public283_cropped.pdf --output_dir outputs --table_format html
```

Ghi chú:
- Nên truyền `--output_dir outputs` rõ ràng để lưu kết quả trong thư mục dự án.
- `--table_format html` giữ bảng ở dạng HTML trong markdown; có thể đổi sang `markdown` nếu cần.

## 4) Cấu trúc output OCR

Sau OCR, mỗi PDF sẽ có thư mục riêng, ví dụ:

```text
outputs/
	Public283/
		main.md
		images/
```

`ocr.py` sẽ tự bỏ hậu tố `_cropped` khi đặt tên thư mục output (ví dụ `Public283_cropped.pdf` -> `outputs/Public283/`).