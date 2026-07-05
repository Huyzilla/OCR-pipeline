from __future__ import annotations

import os
import sys
from importlib import metadata
from typing import Any


def _version(package: str) -> str:
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        return "not installed"


def get_runtime_report() -> dict[str, Any]:
    report: dict[str, Any] = {
        "python": sys.executable,
        "conda_prefix": os.environ.get("CONDA_PREFIX", ""),
        "torch_package": _version("torch"),
        "sentence_transformers_package": _version("sentence-transformers"),
        "streamlit_package": _version("streamlit"),
        "env": {
            "STREAMLIT_SERVER_FILE_WATCHER_TYPE": os.environ.get("STREAMLIT_SERVER_FILE_WATCHER_TYPE", ""),
            "TOKENIZERS_PARALLELISM": os.environ.get("TOKENIZERS_PARALLELISM", ""),
            "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS", ""),
            "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS", ""),
        },
        "checks": {},
    }

    try:
        import torch

        report["checks"]["torch"] = {
            "ok": True,
            "version": torch.__version__,
            "cuda": torch.version.cuda,
            "cuda_available": torch.cuda.is_available(),
        }
    except Exception as exc:
        report["checks"]["torch"] = {"ok": False, "error": repr(exc)}

    try:
        from sentence_transformers import CrossEncoder, SentenceTransformer

        report["checks"]["sentence_transformers"] = {
            "ok": True,
            "SentenceTransformer": SentenceTransformer.__name__,
            "CrossEncoder": CrossEncoder.__name__,
        }
    except Exception as exc:
        report["checks"]["sentence_transformers"] = {"ok": False, "error": repr(exc)}

    return report
