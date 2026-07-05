from __future__ import annotations

import contextlib
import io
import json
import sys
import traceback
from pathlib import Path

from .models import RetrievalSettings
from .paths import CORPUS_CHUNK_DIR, setup_project_paths
from .warmup import warmup_models


setup_project_paths()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    payload = json.load(sys.stdin)
    log_buffer = io.StringIO()

    try:
        settings = RetrievalSettings(**payload["settings"])
        chunk_dir = Path(payload.get("chunk_dir") or CORPUS_CHUNK_DIR)
        doc_scopes = tuple(payload.get("doc_scopes") or ())
        with contextlib.redirect_stdout(log_buffer), contextlib.redirect_stderr(log_buffer):
            result = warmup_models(settings, chunk_dir=chunk_dir, doc_scopes=doc_scopes)
        result["worker"] = {
            "python": sys.executable,
            "log": log_buffer.getvalue(),
        }
        print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                    "log": log_buffer.getvalue(),
                    "python": sys.executable,
                },
                ensure_ascii=False,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
