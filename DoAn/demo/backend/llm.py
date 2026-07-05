from __future__ import annotations

from .models import RetrievalSettings
from .paths import OPENAI_ENV_FILE, setup_project_paths
from .prompts import ANSWER_PROMPT

setup_project_paths()

from qa.openai_client import call_gpt, init_client, load_env_file


def answer_with_llm(
    question: str,
    context: str,
    intent: str,
    settings: RetrievalSettings,
) -> tuple[str, float]:
    load_env_file(OPENAI_ENV_FILE, override=True)
    client = init_client()
    prompt = ANSWER_PROMPT.format(
        question=question,
        context=context or "Không có ngữ cảnh.",
        intent=intent,
    )
    return call_gpt(
        client,
        prompt,
        model=settings.answer_model,
        max_tokens=settings.answer_max_tokens,
        temperature=0,
        max_retries=5,
        retry_delay=2,
    )
