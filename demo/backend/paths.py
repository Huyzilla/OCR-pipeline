from __future__ import annotations

import sys
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEMO_ROOT = PROJECT_ROOT / "demo"
SRC_DIR = PROJECT_ROOT / "src"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

RUNTIME_DIR = DEMO_ROOT / "runtime"
UPLOAD_DIR = RUNTIME_DIR / "uploads"
UPLOAD_OCR_DIR = RUNTIME_DIR / "ocr_outputs"
UPLOAD_CHUNK_DIR = RUNTIME_DIR / "chunks"

CORPUS_OCR_DIR = PROJECT_ROOT / "outputs_1"
CORPUS_CHUNK_DIR = PROJECT_ROOT / "chunk_outputs1_finals"
OPENAI_ENV_FILE = PROJECT_ROOT / ".env"


def setup_project_paths() -> None:
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")

    for path in (PROJECT_ROOT, SRC_DIR, SCRIPTS_DIR):
        text = str(path)
        if text not in sys.path:
            sys.path.insert(0, text)


def ensure_runtime_dirs() -> None:
    for path in (UPLOAD_DIR, UPLOAD_OCR_DIR, UPLOAD_CHUNK_DIR):
        path.mkdir(parents=True, exist_ok=True)


setup_project_paths()
