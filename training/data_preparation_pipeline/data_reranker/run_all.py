from __future__ import annotations

import argparse

try:
    from .pipeline import run_all
except ImportError:
    from pipeline import run_all


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all reranker data stages.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--smoke-n", type=int, default=0)
    args = parser.parse_args()

    run_all(
        dry_run=args.dry_run,
        resume=not args.no_resume,
        smoke_n=args.smoke_n,
    )


if __name__ == "__main__":
    main()
