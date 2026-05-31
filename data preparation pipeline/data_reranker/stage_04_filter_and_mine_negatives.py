from __future__ import annotations

import argparse

try:
    from . import config as cfg
    from .pipeline import run_filter_and_mine_negatives
except ImportError:
    import config as cfg
    from pipeline import run_filter_and_mine_negatives


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 4: filter synthesized and mine negatives.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--n", type=int, default=0)
    parser.add_argument("--answerability-model", default=cfg.ANSWERABILITY_MODEL)
    args = parser.parse_args()

    run_filter_and_mine_negatives(
        dry_run=args.dry_run,
        n=args.n,
        answerability_model=args.answerability_model,
    )


if __name__ == "__main__":
    main()
