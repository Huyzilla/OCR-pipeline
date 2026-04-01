#!/usr/bin/env python3
"""Monitor OCR batch processing progress"""
import subprocess
import time
from pathlib import Path

def get_progress():
    """Get current OCR batch progress"""
    project_root = Path(__file__).resolve().parent
    log_file = project_root / "ocr_batch_cropped.log"
    outputs_dir = project_root / "outputs"
    input_dir = project_root / "input" / "cropped_pdfs"
    total_pdfs = len(list(input_dir.glob("*.pdf"))) if input_dir.exists() else 0
    
    print("\n" + "="*70)
    print("📊 OCR BATCH PROGRESS")
    print("="*70)
    
    # Count completed folders
    if outputs_dir.exists():
        completed_folders = len(list(outputs_dir.glob("Public*")))
        if total_pdfs > 0:
            print(f"✅ Completed folders: {completed_folders}/{total_pdfs}")
        else:
            print(f"✅ Completed folders: {completed_folders}")
    else:
        if total_pdfs > 0:
            print(f"✅ Completed folders: 0/{total_pdfs}")
        else:
            print("✅ Completed folders: 0")

    # Show OCR process status
    proc_cmd = "ps -eo pid,etime,cmd | grep -E 'python(3)? ocr.py|ocr.py --input_dir' | grep -v grep"
    proc = subprocess.run(proc_cmd, shell=True, capture_output=True, text=True)
    proc_lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    if proc_lines:
        print("🏃 OCR process:")
        print(f"  {proc_lines[0]}")
    else:
        print("⏹️  OCR process: not running")

    # Show next pending file based on outputs/<PublicXXX>/main.md
    if input_dir.exists():
        pending = []
        for pdf_path in sorted(input_dir.glob("*.pdf")):
            stem = pdf_path.stem
            folder = stem[:-len("_cropped")] if stem.endswith("_cropped") else stem
            done_md = outputs_dir / folder / "main.md"
            if not (done_md.exists() and done_md.stat().st_size > 0):
                pending.append(pdf_path.name)

        if pending:
            print(f"⏭️  Next pending: {pending[0]}")
            print(f"📌 Remaining: {len(pending)}")
        else:
            print("✅ No pending files")
    
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
