from __future__ import annotations

import argparse

try:
    from .pipeline import run_synthesize_hard_negatives
except ImportError:
    from pipeline import run_synthesize_hard_negatives


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 3: synthesize hard negatives.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--n", type=int, default=0)
    args = parser.parse_args()

    run_synthesize_hard_negatives(
        dry_run=args.dry_run,
        resume=not args.no_resume,
        n=args.n,
    )


if __name__ == "__main__":
    main()
