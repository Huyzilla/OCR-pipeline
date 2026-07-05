from __future__ import annotations

import sys
from pathlib import Path


def setup() -> None:
    frontend_dir = Path(__file__).resolve().parent
    demo_dir = frontend_dir.parent
    project_root = demo_dir.parent
    for path in (demo_dir, project_root, project_root / "src", project_root / "scripts"):
        text = str(path)
        if text not in sys.path:
            sys.path.insert(0, text)


setup()
