from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import RetrievalSettings
from .paths import PROJECT_ROOT, SCRIPTS_DIR, SRC_DIR


def _worker_env() -> dict[str, str]:
    env = os.environ.copy()
    python_paths = [
        str(PROJECT_ROOT / "demo"),
        str(PROJECT_ROOT),
        str(SRC_DIR),
        str(SCRIPTS_DIR),
    ]
    existing = env.get("PYTHONPATH")
    if existing:
        python_paths.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(python_paths)
    env.setdefault("TOKENIZERS_PARALLELISM", "false")
    env.setdefault("OMP_NUM_THREADS", "1")
    env.setdefault("MKL_NUM_THREADS", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")
    return env


def ask_question_in_worker(
    question: str,
    settings: RetrievalSettings,
    *,
    chunk_dir: Path,
    doc_scopes: tuple[str, ...] = (),
    timeout_s: int = 900,
) -> dict[str, Any]:
    payload = {
        "question": question,
        "settings": asdict(settings),
        "chunk_dir": str(chunk_dir),
        "doc_scopes": list(doc_scopes),
    }
    proc = subprocess.run(
        [sys.executable, "-m", "backend.qa_worker"],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(PROJECT_ROOT),
        env=_worker_env(),
        timeout=timeout_s,
    )

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    try:
        response = json.loads(stdout.splitlines()[-1])
    except Exception as exc:
        raise RuntimeError(
            "Worker không trả về JSON hợp lệ.\n"
            f"Return code: {proc.returncode}\n"
            f"STDOUT:\n{stdout[-4000:]}\n"
            f"STDERR:\n{stderr[-4000:]}"
        ) from exc

    if proc.returncode != 0 or not response.get("ok"):
        raise RuntimeError(
            "Worker xử lý lỗi.\n"
            f"Error: {response.get('error')}\n"
            f"Log:\n{response.get('log', '')[-3000:]}\n"
            f"Traceback:\n{response.get('traceback', '')[-3000:]}\n"
            f"STDERR:\n{stderr[-3000:]}"
        )

    result = response["result"]
    if stderr:
        result.setdefault("worker", {})["stderr"] = stderr
    return result


def warmup_models_in_worker(
    settings: RetrievalSettings,
    *,
    chunk_dir: Path,
    doc_scopes: tuple[str, ...] = (),
    timeout_s: int = 900,
) -> dict[str, Any]:
    payload = {
        "settings": asdict(settings),
        "chunk_dir": str(chunk_dir),
        "doc_scopes": list(doc_scopes),
    }
    proc = subprocess.run(
        [sys.executable, "-m", "backend.warmup_worker"],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(PROJECT_ROOT),
        env=_worker_env(),
        timeout=timeout_s,
    )

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    try:
        response = json.loads(stdout.splitlines()[-1])
    except Exception as exc:
        raise RuntimeError(
            "Warmup worker không trả về JSON hợp lệ.\n"
            f"Return code: {proc.returncode}\n"
            f"STDOUT:\n{stdout[-4000:]}\n"
            f"STDERR:\n{stderr[-4000:]}"
        ) from exc

    if proc.returncode != 0 or not response.get("ok"):
        raise RuntimeError(
            "Warmup worker lỗi.\n"
            f"Error: {response.get('error')}\n"
            f"Log:\n{response.get('log', '')[-3000:]}\n"
            f"Traceback:\n{response.get('traceback', '')[-3000:]}\n"
            f"STDERR:\n{stderr[-3000:]}"
        )

    result = response["result"]
    if stderr:
        result.setdefault("worker", {})["stderr"] = stderr
    return result
