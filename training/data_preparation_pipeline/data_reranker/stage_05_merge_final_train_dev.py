from __future__ import annotations

import argparse

try:
    from . import config as cfg
    from .pipeline import run_merge_final_train_dev
except ImportError:
    import config as cfg
    from pipeline import run_merge_final_train_dev


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 5: merge final train/dev triplets.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-easy", type=int, default=cfg.MAX_EASY)
    parser.add_argument("--dev-ratio", type=float, default=cfg.DEV_RATIO)
    parser.add_argument("--seed", type=int, default=cfg.SEED)
    args = parser.parse_args()

    run_merge_final_train_dev(
        dry_run=args.dry_run,
        max_easy=args.max_easy,
        dev_ratio=args.dev_ratio,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
