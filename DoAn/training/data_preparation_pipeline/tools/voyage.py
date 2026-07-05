"""Rerank retrieval candidates in a JSONL file with Voyage AI."""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for path in (start, *start.parents):
        if (path / ".git").exists():
            return path
    return start


ROOT_DIR = find_repo_root(Path(__file__).resolve())
DEFAULT_INPUT = ROOT_DIR / "data" / "retrieve_new_orig.jsonl"
DEFAULT_OUTPUT = ROOT_DIR / "domain_data" / "retrieve_new_orig_voyage.jsonl"
DEFAULT_URL = "https://api.voyageai.com/v1/rerank"
DEFAULT_MODEL = "rerank-2.5"


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_completed_indices(path: Path) -> set[int]:
    completed: set[int] = set()
    if not path.exists():
        return completed

    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                completed.add(int(json.loads(line)["index"]))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid existing output at line {line_number}: {path}"
                ) from exc
    return completed


def call_voyage_rerank(
    *,
    query: str,
    documents: list[str],
    api_key: str,
    api_url: str,
    model: str,
    timeout: float,
    max_retries: int,
) -> list[dict[str, Any]]:
    payload = {
        "model": model,
        "query": query,
        "documents": documents,
        "top_k": len(documents),
        "return_documents": False,
    }
    request = urllib.request.Request(
        api_url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "DATN-Rerank/1.0",
        },
        method="POST",
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    for attempt in range(max_retries + 1):
        try:
            with opener.open(request, timeout=timeout) as response:
                body = response.read().decode("utf-8")
            data = json.loads(body)
            results = data.get("data") or data.get("results")
            if not isinstance(results, list):
                raise RuntimeError("Voyage response does not contain a results list")
            return results
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            error = RuntimeError(f"Voyage HTTP {exc.code}: {body[:500]}")
            retryable = exc.code == 429 or exc.code >= 500
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            error = RuntimeError(f"Voyage request failed: {exc}")
            retryable = True

        if attempt >= max_retries or not retryable:
            raise error
        time.sleep(min(60, 2 ** (attempt + 1)))

    raise RuntimeError("Voyage request failed")


def rerank_record(
    record: dict[str, Any],
    *,
    api_key: str,
    api_url: str,
    model: str,
    timeout: float,
    max_retries: int,
) -> dict[str, Any]:
    candidates = record.get("candidates", [])
    if not isinstance(candidates, list) or not candidates:
        raise ValueError(f"Index {record.get('index')}: candidates are missing")

    documents = [str(candidate.get("chunk", "")).strip() for candidate in candidates]
    if any(not document for document in documents):
        raise ValueError(f"Index {record.get('index')}: candidate chunk text is missing")

    results = call_voyage_rerank(
        query=str(record.get("question", "")).strip(),
        documents=documents,
        api_key=api_key,
        api_url=api_url,
        model=model,
        timeout=timeout,
        max_retries=max_retries,
    )

    ranked_candidates: list[dict[str, Any]] = []
    seen_indices: set[int] = set()
    for item in results:
        try:
            source_index = int(item["index"])
            score = float(item.get("relevance_score", item.get("score", 0.0)))
        except (KeyError, TypeError, ValueError):
            continue
        if source_index < 0 or source_index >= len(candidates):
            continue
        if source_index in seen_indices:
            continue

        candidate = dict(candidates[source_index])
        candidate["source_rank"] = candidate.get("rank", source_index)
        candidate["rank"] = len(ranked_candidates)
        candidate["voyage_score"] = score
        ranked_candidates.append(candidate)
        seen_indices.add(source_index)

    if len(ranked_candidates) != len(candidates):
        raise RuntimeError(
            f"Index {record.get('index')}: Voyage returned "
            f"{len(ranked_candidates)}/{len(candidates)} valid candidates"
        )

    output = dict(record)
    output["rerank_model"] = model
    output["candidates"] = ranked_candidates
    return output


def count_jsonl(path: Path) -> int:
    with path.open("r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rerank every candidate list in a retrieval JSONL with Voyage AI."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--api-url", default=None)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--n", type=int, default=0, help="Process at most N new rows.")
    parser.add_argument("--no-resume", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_dotenv(ROOT_DIR / ".env")

    api_key = os.getenv("VOYAGE_API_KEY", "").strip()
    api_url = (
        args.api_url
        or os.getenv("VOYAGE_RERANK_URL", "").strip()
        or DEFAULT_URL
    )
    if not api_key:
        raise RuntimeError("VOYAGE_API_KEY is missing from environment or .env")
    if not args.input.exists():
        raise FileNotFoundError(f"Input file not found: {args.input}")

    if args.no_resume and args.output.exists():
        raise FileExistsError(
            f"Output already exists: {args.output}. Remove it or use resume mode."
        )

    completed = set() if args.no_resume else load_completed_indices(args.output)
    total_rows = count_jsonl(args.input)
    target_rows = total_rows if args.n <= 0 else min(total_rows, len(completed) + args.n)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if args.no_resume else "a"
    processed = 0
    started = time.perf_counter()

    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Model: {args.model}")
    print(f"Rows: {total_rows} | Resume completed: {len(completed)}")

    with args.input.open("r", encoding="utf-8") as source, args.output.open(
        mode, encoding="utf-8"
    ) as destination:
        for line in source:
            if not line.strip():
                continue
            record = json.loads(line)
            index = int(record["index"])
            if index in completed:
                continue
            if args.n > 0 and processed >= args.n:
                break

            reranked = rerank_record(
                record,
                api_key=api_key,
                api_url=api_url,
                model=args.model,
                timeout=args.timeout,
                max_retries=args.max_retries,
            )
            destination.write(json.dumps(reranked, ensure_ascii=False) + "\n")
            destination.flush()

            processed += 1
            done = len(completed) + processed
            elapsed = time.perf_counter() - started
            seconds_per_row = elapsed / processed
            eta_minutes = max(0, target_rows - done) * seconds_per_row / 60
            top = reranked["candidates"][0]
            print(
                f"[{done:>3}/{target_rows}] Q{index:>3} "
                f"top={top['chunk_id']} score={top['voyage_score']:.4f} "
                f"ETA={eta_minutes:.1f}m",
                flush=True,
            )

    print(f"Completed new rows: {processed}")
    print(f"Total output rows: {len(completed) + processed}")


if __name__ == "__main__":
    main()
