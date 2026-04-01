#!/usr/bin/env python3
"""Quick OCR batch progress checker"""
import subprocess
from pathlib import Path

def check_ocr_progress():
    """Check OCR batch progress"""
    outputs_dir = Path("/media/data3/users/huytq/huy/outputs")
    if not outputs_dir.exists():
        print("❌ Output folder not found yet")
        return
    
    # Count completed folders
    completed = len(list(outputs_dir.iterdir()))
    print(f"✅ Completed folders: {completed}")
    
    # Check log file
    log_file = Path("/media/data3/users/huytq/huy/ocr_batch.log")
    if log_file.exists():
        with open(log_file, "r") as f:
            last_lines = f.readlines()[-3:]
            print("\n📋 Last log lines:")
            for line in last_lines:
                print(f"  {line.rstrip()}")

if __name__ == "__main__":
    check_ocr_progress()
