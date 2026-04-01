#!/usr/bin/env python3
"""Quick OCR batch progress checker"""
from pathlib import Path

def check_ocr_progress():
    """Check OCR batch progress"""
    project_root = Path(__file__).resolve().parent
    outputs_dir = project_root / "outputs"
    input_dir = project_root / "input" / "cropped_pdfs"

    total_pdfs = len(list(input_dir.glob("*.pdf"))) if input_dir.exists() else 0

    if not outputs_dir.exists():
        print("❌ Output folder not found yet")
        return
    
    # Count completed folders
    completed = len(list(outputs_dir.glob("Public*")))
    if total_pdfs > 0:
        print(f"✅ Completed folders: {completed}/{total_pdfs}")
    else:
        print(f"✅ Completed folders: {completed}")
    
    # Check log file
    log_file = project_root / "ocr_batch_cropped.log"
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            last_lines = f.readlines()[-3:]
            print("\n📋 Last log lines:")
            for line in last_lines:
                print(f"  {line.rstrip()}")
    else:
        print("\n⏳ Log file chưa có hoặc chưa ghi dữ liệu")

if __name__ == "__main__":
    check_ocr_progress()
