from __future__ import annotations

import os
import re
import time
from pathlib import Path


def mask_secret(value: str) -> str:
    if len(value) <= 12:
        return "***"
    return f"{value[:7]}...{value[-4:]}"


def load_env_file(path: Path, *, override: bool = True) -> None:
    if not path.exists():
        return

    loaded = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and (override or key not in os.environ):
                os.environ[key] = value
                loaded.append(key)

    if "OPENAI_API_KEY" in loaded:
        print(f"Loaded OPENAI_API_KEY from {path} ({mask_secret(os.environ['OPENAI_API_KEY'])})")


def require_openai_key() -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not found.")
    return api_key


def init_client():
    from openai import OpenAI

    return OpenAI(api_key=require_openai_key())


def call_gpt(
    client,
    prompt: str,
    *,
    model: str,
    max_tokens: int,
    temperature: float,
    max_retries: int,
    retry_delay: float,
) -> tuple[str, float]:
    t0 = time.time()
    for attempt in range(1, max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return resp.choices[0].message.content.strip(), time.time() - t0
        except Exception as exc:
            err = str(exc)
            wait = retry_delay * (2 ** (attempt - 1))
            match = re.search(r"try again in (\d+(?:\.\d+)?)(ms|s)", err)
            if match:
                value = float(match.group(1))
                unit = match.group(2)
                wait = (value / 1000 if unit == "ms" else value) + 1.5

            short_err = err.replace("\n", " ")[:300]
            if "401" in err or "Incorrect API key" in err:
                print(f"\n  [ERROR] GPT auth failed: {short_err}")
                return "", time.time() - t0
            if attempt == max_retries:
                print(f"\n  [ERROR] GPT failed after {max_retries} attempts: {short_err}")
                return "", time.time() - t0

            print(f"\n  [WARN] GPT attempt {attempt} failed: {short_err}")
            print(f"         waiting {wait:.1f}s...")
            time.sleep(wait)

    return "", time.time() - t0
