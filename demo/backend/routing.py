from __future__ import annotations

import time
from functools import lru_cache
from pathlib import Path

from .models import RetrievalSettings
from .paths import OPENAI_ENV_FILE, setup_project_paths
from .prompts import ROUTER_PROMPT

setup_project_paths()

from qa.openai_client import call_gpt, init_client, load_env_file


def clean_question_text(text: str) -> str:
    # pyvi/pycrfsuite cannot handle lone surrogate code points.
    cleaned = str(text).encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
    return " ".join(cleaned.split())


def route_question(question: str, settings: RetrievalSettings) -> tuple[str, float]:
    if settings.router_kind == "none":
        return "tra_cuu", 0.0
    if settings.router_kind == "sbert":
        return route_question_sbert(question, settings.router_model)
    return route_question_gpt(question, settings.router_model)


def route_question_gpt(question: str, model: str) -> tuple[str, float]:
    load_env_file(OPENAI_ENV_FILE, override=True)
    client = init_client()
    question = clean_question_text(question)
    raw, elapsed = call_gpt(
        client,
        ROUTER_PROMPT.format(question=question),
        model=model,
        max_tokens=16,
        temperature=0,
        max_retries=3,
        retry_delay=2,
    )
    text = (raw or "").strip().lower()
    if "tinh_toan" in text or "tính toán" in text:
        return "tinh_toan", elapsed
    return "tra_cuu", elapsed


@lru_cache(maxsize=2)
def load_sbert_router(model_dir: str):
    from run_baseline_gist_minilm import SbertIntentRouter

    return SbertIntentRouter(Path(model_dir))


def route_question_sbert(question: str, model_dir: str) -> tuple[str, float]:
    t0 = time.perf_counter()
    router = load_sbert_router(model_dir)
    try:
        intent, _public_ids, elapsed = router.route({"question": clean_question_text(question)})
        return intent, elapsed or (time.perf_counter() - t0)
    except Exception as exc:
        print(f"[WARN] SBERT router failed, fallback to tra_cuu: {exc}")
        return "tra_cuu", time.perf_counter() - t0
