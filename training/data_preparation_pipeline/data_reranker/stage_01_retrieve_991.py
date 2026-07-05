from __future__ import annotations

import argparse

try:
    from . import config as cfg
    from .pipeline import run_retrieve_991
except ImportError:
    import config as cfg
    from pipeline import run_retrieve_991


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 1: retrieve + rerank 991 questions.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--top-k", type=int, default=cfg.TOP_K)
    parser.add_argument("--embedding-model", default=cfg.EMBEDDING_MODEL)
    parser.add_argument("--rerank-model", default=cfg.RERANK_MODEL)
    args = parser.parse_args()

    run_retrieve_991(
        dry_run=args.dry_run,
        resume=not args.no_resume,
        top_k=args.top_k,
        embedding_model=args.embedding_model,
        rerank_model=args.rerank_model,
    )


if __name__ == "__main__":
    main()
