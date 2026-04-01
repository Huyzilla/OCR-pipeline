#!/usr/bin/env python3
"""Monitor OCR batch processing progress"""
import time
import subprocess
from pathlib import Path
import re

def get_progress():
    """Get current OCR batch progress"""
    log_file = Path("/media/data3/users/huytq/huy/ocr_batch_cropped.log")
    outputs_dir = Path("/media/data3/users/huytq/huy/outputs")
    
    print("\n" + "="*70)
    print("📊 OCR BATCH PROGRESS")
    print("="*70)
    
    # Count completed folders
    if outputs_dir.exists():
        completed_folders = len(list(outputs_dir.iterdir()))
        print(f"✅ Completed folders: {completed_folders}/206")
    else:
        print(f"✅ Completed folders: 0/206")
    
    # Parse log
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Get last few lines
        last_10 = lines[-10:] if len(lines) > 10 else lines
        
        # Find processing line
        for line in reversed(lines[-20:]):
            if "Processing:" in line:
                print(f"\n📍 Current: {line.strip()}")
                break
        
        # Count success/fail
        success = len([l for l in lines if "✅" in l])
        failed = len([l for l in lines if "❌" in l and "ERROR" in l])
        
        if success > 0 or failed > 0:
            print(f"✅ Success: {success} | ❌ Failed: {failed}")
        
        # Show last log line
        if lines:
            print(f"\n📋 Last log:\n  {lines[-1].strip()}")
    else:
        print("⏳ Waiting for log file...")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "watch":
        # Watch mode - refresh every 30 seconds
        print("🔄 Watching OCR progress (Ctrl+C to stop)...")
        try:
            while True:
                get_progress()
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n⏹️  Stopped watching")
    else:
        get_progress()
