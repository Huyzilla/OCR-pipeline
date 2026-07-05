from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from . import config as cfg
    from .pipeline import STAGE_INFO, STAGE_ORDER, run_stage
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent))
    import config as cfg
    from pipeline import STAGE_INFO, STAGE_ORDER, run_stage


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run reranker training-data stages.")
    parser.add_argument("stage", nargs="?", default="status", choices=["status", "all", *STAGE_ORDER])
    parser.add_argument("--from-stage", choices=STAGE_ORDER)
    parser.add_argument("--to-stage", choices=STAGE_ORDER)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--smoke-n", type=int, default=0, help="Limit GPT stages for a quick test.")
    parser.add_argument("--top-k", type=int, default=cfg.TOP_K)
    parser.add_argument("--max-easy", type=int, default=cfg.MAX_EASY)
    parser.add_argument("--dev-ratio", type=float, default=cfg.DEV_RATIO)
    parser.add_argument("--seed", type=int, default=cfg.SEED)
    parser.add_argument("--embedding-model", default=cfg.EMBEDDING_MODEL)
    parser.add_argument("--rerank-model", default=cfg.RERANK_MODEL)
    parser.add_argument("--answerability-model", default=cfg.ANSWERABILITY_MODEL)
    return parser.parse_args()


def stages_to_run(args: argparse.Namespace) -> list[str]:
    if args.stage == "status":
        return []
    if args.stage != "all":
        return [args.stage]

    start = STAGE_ORDER.index(args.from_stage) if args.from_stage else 0
    end = STAGE_ORDER.index(args.to_stage) if args.to_stage else len(STAGE_ORDER) - 1
    if start > end:
        raise SystemExit("--from-stage must come before --to-stage")
    return list(STAGE_ORDER[start : end + 1])


def print_status() -> None:
    print("Reranker fine-tuning data pipeline\n")
    for i, stage in enumerate(STAGE_ORDER, 1):
        info = STAGE_INFO[stage]
        print(f"{i}. {stage}")
        print(f"   {info['title']}")
        print(f"   output: {info['output']}")
        print()


def main() -> int:
    args = parse_args()

    if args.stage == "status":
        print_status()
        return 0

    for stage in stages_to_run(args):
        run_stage(
            stage,
            dry_run=args.dry_run,
            resume=not args.no_resume,
            smoke_n=args.smoke_n,
            top_k=args.top_k,
            max_easy=args.max_easy,
            dev_ratio=args.dev_ratio,
            seed=args.seed,
            embedding_model=args.embedding_model,
            rerank_model=args.rerank_model,
            answerability_model=args.answerability_model,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
