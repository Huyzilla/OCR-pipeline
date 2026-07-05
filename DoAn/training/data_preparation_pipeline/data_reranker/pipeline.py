from __future__ import annotations

try:
    from . import config as cfg
    from .common import require_openai_key, run_python
except ImportError:
    import config as cfg
    from common import require_openai_key, run_python


STAGE_ORDER = ("retrieve", "judge_gold", "synthesize", "filter_and_mine", "merge")

STAGE_INFO = {
    "retrieve": {
        "title": "Stage 1: retrieve 991 questions + BGE rerank",
        "output": cfg.RETRIEVE_OUTPUT,
    },
    "judge_gold": {
        "title": "Stage 2: GPT judge gold chunks",
        "output": cfg.JUDGED_OUTPUT,
    },
    "synthesize": {
        "title": "Stage 3: synthesize hard negatives",
        "output": cfg.SYNTHESIZED_OUTPUT,
    },
    "filter_and_mine": {
        "title": "Stage 4: verify synthesized + mine negatives",
        "output": f"{cfg.SYNTHESIZED_FILTERED_OUTPUT} + {cfg.MINED_OUTPUT}",
    },
    "merge": {
        "title": "Stage 5: merge final train/dev",
        "output": f"{cfg.TRAIN_OUTPUT} + {cfg.DEV_OUTPUT}",
    },
}


def run_retrieve_991(
    *,
    dry_run: bool = False,
    resume: bool = True,
    embedding_model: str = cfg.EMBEDDING_MODEL,
    rerank_model: str = cfg.RERANK_MODEL,
    top_k: int = cfg.TOP_K,
) -> None:
    # 991 questions -> hybrid retrieval -> BGE rerank -> top-k candidates.
    run_python(
        "Stage 1 - Retrieve 991 questions + BGE rerank",
        cfg.PIPELINE_DIR / "retrieve_rerank_991.py",
        args={
            "question_csv": cfg.QUESTION_CSV,
            "intent_csv": cfg.INTENT_CSV,
            "chunk_dir": cfg.CHUNK_DIR,
            "chroma_path": cfg.CHROMA_PATH,
            "output": cfg.RETRIEVE_OUTPUT,
            "embedding_model": embedding_model,
            "rerank_model": rerank_model,
            "top_k": top_k,
        },
        flags=["resume"] if resume else [],
        dry_run=dry_run,
    )


def run_judge_gold_chunks(
    *,
    dry_run: bool = False,
    resume: bool = True,
    n: int = 0,
    offset: int = 0,
) -> None:
    # GPT labels top candidates as gold / partial / irrelevant.
    if not dry_run:
        require_openai_key("Stage 2")

    run_python(
        "Stage 2 - GPT judge gold chunks",
        cfg.PIPELINE_DIR / "gpt_judge_gold_chunks.py",
        args={
            "input": cfg.RETRIEVE_OUTPUT,
            "output": cfg.JUDGED_OUTPUT,
            "n": n,
            "offset": offset,
        },
        flags=["resume"] if resume else [],
        dry_run=dry_run,
    )


def run_synthesize_hard_negatives(
    *,
    dry_run: bool = False,
    resume: bool = True,
    n: int = 0,
) -> None:
    # GPT rewrites gold chunks into subtle false negatives.
    if not dry_run:
        require_openai_key("Stage 3")

    run_python(
        "Stage 3 - Synthesize hard negatives",
        cfg.PIPELINE_DIR / "synthesize_negatives_v2.py",
        args={
            "judged": cfg.JUDGED_OUTPUT,
            "output": cfg.SYNTHESIZED_OUTPUT,
            "n": n,
        },
        flags=["resume"] if resume else [],
        dry_run=dry_run,
    )


def run_verify_synthesized_negatives(
    *,
    dry_run: bool = False,
    n: int = 0,
    model: str = cfg.ANSWERABILITY_MODEL,
    max_chars: int = 5000,
    use_cache: bool = True,
    keep_empty: bool = False,
) -> None:
    # Independent GPT judge removes synthesized negatives that still answer the query.
    if not dry_run:
        require_openai_key("Stage 4a")

    args = {
        "input": cfg.SYNTHESIZED_OUTPUT,
        "output": cfg.SYNTHESIZED_FILTERED_OUTPUT,
        "removed": cfg.SYNTHESIZED_REMOVED_OUTPUT,
        "model": model,
        "n": n,
        "max_chars": max_chars,
    }
    flags = []

    if use_cache:
        args["cache"] = cfg.ANSWERABILITY_CACHE
    else:
        flags.append("no_cache")

    if keep_empty:
        flags.append("keep_empty")

    run_python(
        "Stage 4a - Verify synthesized negatives",
        cfg.PIPELINE_DIR / "filter_synthesized_negatives_answerability.py",
        args=args,
        flags=flags,
        dry_run=dry_run,
    )


def run_extract_mined_negatives(*, dry_run: bool = False) -> None:
    # Mine hard/medium/easy negatives from non-gold rerank candidates.
    run_python(
        "Stage 4b - Extract mined negatives",
        cfg.PIPELINE_DIR / "extract_mined_negatives.py",
        args={
            "judged": cfg.JUDGED_OUTPUT,
            "retrieve": cfg.RETRIEVE_OUTPUT,
            "output": cfg.MINED_OUTPUT,
        },
        dry_run=dry_run,
    )


def run_filter_and_mine_negatives(
    *,
    dry_run: bool = False,
    n: int = 0,
    answerability_model: str = cfg.ANSWERABILITY_MODEL,
) -> None:
    run_verify_synthesized_negatives(
        dry_run=dry_run,
        n=n,
        model=answerability_model,
    )
    run_extract_mined_negatives(dry_run=dry_run)


def run_merge_final_train_dev(
    *,
    dry_run: bool = False,
    max_easy: int = cfg.MAX_EASY,
    dev_ratio: float = cfg.DEV_RATIO,
    seed: int = cfg.SEED,
) -> None:
    # Keep synthesized + mined hard/medium negatives, then split by query.
    run_python(
        "Stage 5 - Merge final train/dev triplets",
        cfg.PIPELINE_DIR / "merge_training_data.py",
        args={
            "synthesized": cfg.SYNTHESIZED_FILTERED_OUTPUT,
            "mined": cfg.MINED_OUTPUT,
            "output_dir": cfg.DOMAIN_DATA,
            "max_easy": max_easy,
            "dev_ratio": dev_ratio,
            "seed": seed,
        },
        dry_run=dry_run,
    )


def run_stage(
    stage: str,
    *,
    dry_run: bool = False,
    resume: bool = True,
    smoke_n: int = 0,
    top_k: int = cfg.TOP_K,
    max_easy: int = cfg.MAX_EASY,
    dev_ratio: float = cfg.DEV_RATIO,
    seed: int = cfg.SEED,
    embedding_model: str = cfg.EMBEDDING_MODEL,
    rerank_model: str = cfg.RERANK_MODEL,
    answerability_model: str = cfg.ANSWERABILITY_MODEL,
) -> None:
    if stage == "retrieve":
        run_retrieve_991(
            dry_run=dry_run,
            resume=resume,
            embedding_model=embedding_model,
            rerank_model=rerank_model,
            top_k=top_k,
        )
    elif stage == "judge_gold":
        run_judge_gold_chunks(dry_run=dry_run, resume=resume, n=smoke_n)
    elif stage == "synthesize":
        run_synthesize_hard_negatives(dry_run=dry_run, resume=resume, n=smoke_n)
    elif stage == "filter_and_mine":
        run_filter_and_mine_negatives(
            dry_run=dry_run,
            n=smoke_n,
            answerability_model=answerability_model,
        )
    elif stage == "merge":
        run_merge_final_train_dev(
            dry_run=dry_run,
            max_easy=max_easy,
            dev_ratio=dev_ratio,
            seed=seed,
        )
    else:
        raise KeyError(f"Unknown stage: {stage}")


def run_all(
    *,
    dry_run: bool = False,
    resume: bool = True,
    smoke_n: int = 0,
    top_k: int = cfg.TOP_K,
    max_easy: int = cfg.MAX_EASY,
    dev_ratio: float = cfg.DEV_RATIO,
    seed: int = cfg.SEED,
    embedding_model: str = cfg.EMBEDDING_MODEL,
    rerank_model: str = cfg.RERANK_MODEL,
    answerability_model: str = cfg.ANSWERABILITY_MODEL,
) -> None:
    for stage in STAGE_ORDER:
        run_stage(
            stage,
            dry_run=dry_run,
            resume=resume,
            smoke_n=smoke_n,
            top_k=top_k,
            max_easy=max_easy,
            dev_ratio=dev_ratio,
            seed=seed,
            embedding_model=embedding_model,
            rerank_model=rerank_model,
            answerability_model=answerability_model,
        )


if __name__ == "__main__":
    run_all()
