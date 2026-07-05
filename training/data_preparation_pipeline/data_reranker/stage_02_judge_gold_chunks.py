from __future__ import annotations

import argparse

try:
    from .pipeline import run_judge_gold_chunks
except ImportError:
    from pipeline import run_judge_gold_chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 2: GPT judge gold chunks.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--n", type=int, default=0)
    parser.add_argument("--offset", type=int, default=0)
    args = parser.parse_args()

    run_judge_gold_chunks(
        dry_run=args.dry_run,
        resume=not args.no_resume,
        n=args.n,
        offset=args.offset,
    )


if __name__ == "__main__":
    main()
