from __future__ import annotations

import sys
from pathlib import Path


def setup_paths() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts"
    src_dir = repo_root / "src"
    for path in (scripts_dir, src_dir, repo_root):
        path_str = str(path)
        if path.exists() and path_str not in sys.path:
            sys.path.insert(0, path_str)
