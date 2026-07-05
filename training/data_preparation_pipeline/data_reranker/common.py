from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Mapping, Sequence

try:
    from .config import PIPELINE_ROOT
except ImportError:
    from config import PIPELINE_ROOT


def require_openai_key(stage_name: str) -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit(f"{stage_name}: OPENAI_API_KEY is not set")


def run_python(
    title: str,
    script: Path,
    args: Mapping[str, object] | None = None,
    flags: Sequence[str] = (),
    *,
    dry_run: bool = False,
) -> None:
    command: list[str] = [sys.executable, str(script)]

    for name, value in (args or {}).items():
        if value is None:
            continue
        command.extend([f"--{name.replace('_', '-')}", str(value)])

    for flag in flags:
        command.append(f"--{flag.replace('_', '-')}")

    print(f"\n{title}")
    print(subprocess.list2cmdline(command))

    if dry_run:
        return

    subprocess.run(command, cwd=PIPELINE_ROOT, check=True)
