#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Independent answerability judge for synthesized hard negatives.

For each (query, negative_chunk), call a separate GPT judge:
    "Does this chunk answer the query?"

If the judge says YES, remove that negative version from the output.
The script also writes an audit JSONL with all removed versions.

Usage:
    python filter_synthesized_negatives_answerability.py \
        --input   domain_data/synthesized_negatives.jsonl \
        --output  domain_data/synthesized_negatives_filtered.jsonl \
        --removed domain_data/synthesized_negatives_removed_answerable.jsonl

Notes:
    - Requires OPENAI_API_KEY.
    - Uses a cache JSONL so re-runs do not call GPT again for already judged
      (index, positive_chunk_id, version_index, text_hash) pairs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any

from openai import OpenAI


DEFAULT_MODEL = "gpt-4o-mini"
MAX_RETRIES = 5
TEMPERATURE = 0
MAX_TOKENS = 160

SYSTEM_PROMPT = """Bạn là judge độc lập để kiểm tra khả năng trả lời của hard negative trong dữ liệu huấn luyện RAG tiếng Việt.

Nhiệm vụ: Với một QUERY và một CANDIDATE CHUNK, quyết định xem đoạn này có trả lời được query hay không.

Trả về answers_query=true nếu đoạn văn chứa đủ thông tin để trả lời trực tiếp query,
hoặc nếu đáp án có thể được suy ra rõ ràng từ đoạn văn.

Trả về answers_query=false nếu đoạn văn chỉ liên quan cùng chủ đề, có chi tiết sai/mâu thuẫn,
thiếu thông tin then chốt, hoặc không trả lời được query.

Hãy đánh giá nghiêm ngặt: hard negative hợp lệ là đoạn KHÔNG trả lời được query.

JSON only:
{"answers_query": true|false, "confidence": "high|medium|low", "reason": "..."}"""


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at {path}:{line_no}: {exc}") from exc
    return entries


def append_jsonl(path: Path, item: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_jsonl(path: Path, entries: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def cache_key(index: Any, positive_chunk_id: str, version_index: int, text: str) -> str:
    return f"{index}\t{positive_chunk_id}\t{version_index}\t{text_hash(text)}"


def load_cache(path: Path | None) -> dict[str, dict[str, Any]]:
    if not path or not path.exists():
        return {}

    cache: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            key = item.get("cache_key")
            if key:
                cache[str(key)] = item
    return cache


def clean_json_string(raw: str) -> str:
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    return match.group(0) if match else ""


def coerce_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"yes", "true", "1", "y"}:
            return True
        if normalized in {"no", "false", "0", "n"}:
            return False
    return None


def truncate_text(text: str, max_chars: int) -> str:
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    half = max_chars // 2
    return (
        text[:half]
        + "\n\n[...TRUNCATED FOR JUDGE...]\n\n"
        + text[-half:]
    )


def build_prompt(query: str, chunk: str, max_chars: int) -> str:
    chunk_for_judge = truncate_text(chunk, max_chars)
    return (
        f"QUERY:\n{query}\n\n"
        f"CANDIDATE CHUNK:\n{chunk_for_judge}\n\n"
        "Câu hỏi kiểm tra: Đoạn CANDIDATE CHUNK có trả lời được QUERY không?\n"
        "Chỉ trả về JSON theo schema đã yêu cầu."
    )


def call_judge(
    client: OpenAI,
    model: str,
    query: str,
    chunk: str,
    max_chars: int,
) -> dict[str, Any]:
    prompt = build_prompt(query, chunk, max_chars=max_chars)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                timeout=30,
            )
            raw = (resp.choices[0].message.content or "").strip()
            cleaned = clean_json_string(raw)
            if cleaned:
                parsed = json.loads(cleaned)
                answers_query = coerce_bool(parsed.get("answers_query"))
                if answers_query is None:
                    return {
                        "answers_query": None,
                        "confidence": parsed.get("confidence", "low"),
                        "reason": "answers_query missing or invalid",
                        "raw": raw,
                        "error": "invalid_answers_query",
                    }
                return {
                    "answers_query": answers_query,
                    "confidence": parsed.get("confidence", "low"),
                    "reason": str(parsed.get("reason", ""))[:500],
                    "raw": raw,
                    "error": None,
                }

            # Last-resort parser for accidental plain Yes/No responses.
            lowered = raw.lower()
            if lowered.startswith("yes"):
                return {
                    "answers_query": True,
                    "confidence": "medium",
                    "reason": "plain yes response",
                    "raw": raw,
                    "error": None,
                }
            if lowered.startswith("no"):
                return {
                    "answers_query": False,
                    "confidence": "medium",
                    "reason": "plain no response",
                    "raw": raw,
                    "error": None,
                }

            return {
                "answers_query": None,
                "confidence": "low",
                "reason": "no parseable JSON/Yes/No",
                "raw": raw,
                "error": "parse_error",
            }

        except json.JSONDecodeError as exc:
            return {
                "answers_query": None,
                "confidence": "low",
                "reason": f"json parse error: {exc}",
                "raw": "",
                "error": "json_parse_error",
            }
        except Exception as exc:
            err = str(exc)
            if "401" in err:
                return {
                    "answers_query": None,
                    "confidence": "low",
                    "reason": "auth error",
                    "raw": "",
                    "error": "auth_error",
                }

            wait = 2 * (2 ** (attempt - 1))
            match = re.search(r"try again in (\d+(?:\.\d+)?)(ms|s)", err)
            if match:
                val, unit = float(match.group(1)), match.group(2)
                wait = (val / 1000 if unit == "ms" else val) + 1.5

            if attempt == MAX_RETRIES:
                return {
                    "answers_query": None,
                    "confidence": "low",
                    "reason": err[:500],
                    "raw": "",
                    "error": "max_retries",
                }
            print(f"    [retry {attempt}] {wait:.1f}s")
            time.sleep(wait)

    return {
        "answers_query": None,
        "confidence": "low",
        "reason": "unreachable max retries",
        "raw": "",
        "error": "max_retries",
    }


def strip_heavy_judge_fields(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "answers_query": result.get("answers_query"),
        "confidence": result.get("confidence"),
        "reason": result.get("reason"),
        "error": result.get("error"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Filter synthesized negatives using an independent GPT answerability judge."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("domain_data/synthesized_negatives.jsonl"),
        help="Input synthesized negatives JSONL.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("domain_data/synthesized_negatives_answerability_filtered.jsonl"),
        help="Output JSONL after removing answerable negatives.",
    )
    parser.add_argument(
        "--removed",
        type=Path,
        default=Path("domain_data/synthesized_negatives_removed_answerable.jsonl"),
        help="Audit JSONL for removed negative versions.",
    )
    parser.add_argument(
        "--cache",
        type=Path,
        default=Path("domain_data/answerability_judge_cache.jsonl"),
        help="Cache JSONL for judge calls. Set --no-cache to disable.",
    )
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--n", type=int, default=0, help="Limit input entries for a smoke run.")
    parser.add_argument(
        "--max-chars",
        type=int,
        default=12000,
        help="Max chunk chars sent to judge; <=0 sends full text.",
    )
    parser.add_argument(
        "--keep-empty",
        action="store_true",
        help="Keep entries even if all valid_negatives are removed.",
    )
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set")
        return 1

    entries = load_jsonl(args.input)
    if args.n > 0:
        entries = entries[: args.n]

    cache_path = None if args.no_cache else args.cache
    cache = load_cache(cache_path)
    client = OpenAI(api_key=api_key)

    kept_entries: list[dict[str, Any]] = []
    removed_items: list[dict[str, Any]] = []

    n_versions = 0
    n_kept = 0
    n_removed = 0
    n_errors = 0
    n_cached = 0
    t_start = time.time()

    for entry_i, entry in enumerate(entries, 1):
        query = str(entry.get("question", ""))
        index = entry.get("index")
        positive_chunk_id = str(entry.get("positive_chunk_id") or "")
        versions = entry.get("valid_negatives") or []

        kept_versions = []

        for version_i, version in enumerate(versions, 1):
            text = str(version.get("text", ""))
            if not text.strip():
                continue

            n_versions += 1
            key = cache_key(index, positive_chunk_id, version_i, text)

            if key in cache:
                judge_result = cache[key]
                n_cached += 1
            else:
                judge_result = call_judge(
                    client=client,
                    model=args.model,
                    query=query,
                    chunk=text,
                    max_chars=args.max_chars,
                )
                judge_result = {
                    "cache_key": key,
                    "index": index,
                    "positive_chunk_id": positive_chunk_id,
                    "version_index": version_i,
                    "text_hash": text_hash(text),
                    "judge": strip_heavy_judge_fields(judge_result),
                }
                if cache_path:
                    append_jsonl(cache_path, judge_result)
                cache[key] = judge_result

            judge = judge_result.get("judge", judge_result)
            answers_query = judge.get("answers_query")
            has_error = bool(judge.get("error"))

            if has_error or answers_query is None:
                # Conservative choice: keep on judge failure, but mark for review.
                n_errors += 1
                version_out = dict(version)
                version_out["source_version_index"] = version_i
                version_out["negative_text_hash"] = text_hash(text)
                version_out["answerability_judge"] = judge
                version_out["needs_answerability_review"] = True
                kept_versions.append(version_out)
                n_kept += 1
                continue

            if answers_query is True:
                removed = {
                    "index": index,
                    "question": query,
                    "positive_chunk_id": positive_chunk_id,
                    "version_index": version_i,
                    "negative_text_hash": text_hash(text),
                    "edit_type": version.get("edit_type"),
                    "judge": judge,
                    "removed_text": text,
                }
                removed_items.append(removed)
                n_removed += 1
                continue

            version_out = dict(version)
            version_out["source_version_index"] = version_i
            version_out["negative_text_hash"] = text_hash(text)
            version_out["answerability_judge"] = judge
            kept_versions.append(version_out)
            n_kept += 1

        if kept_versions or args.keep_empty:
            entry_out = dict(entry)
            entry_out["valid_negatives"] = kept_versions
            entry_out["n_valid"] = len(kept_versions)
            entry_out["answerability_filter"] = {
                "model": args.model,
                "original_n_valid": len(versions),
                "removed": len(versions) - len(kept_versions),
            }
            kept_entries.append(entry_out)

        if entry_i % 25 == 0 or entry_i == len(entries):
            elapsed = time.time() - t_start
            per_entry = elapsed / entry_i
            remain = (len(entries) - entry_i) * per_entry
            print(
                f"[{entry_i}/{len(entries)}] versions={n_versions} "
                f"kept={n_kept} removed={n_removed} errors={n_errors} "
                f"cached={n_cached} ETA={remain/60:.1f}min"
            )

    write_jsonl(args.output, kept_entries)
    write_jsonl(args.removed, removed_items)

    print("\nDONE")
    print(f"Input entries:       {len(entries)}")
    print(f"Output entries:      {len(kept_entries)}")
    print(f"Negative versions:   {n_versions}")
    print(f"Kept versions:       {n_kept}")
    print(f"Removed answerable:  {n_removed}")
    print(f"Judge errors kept:   {n_errors}")
    print(f"Cache hits:          {n_cached}")
    print(f"Output:              {args.output}")
    print(f"Removed audit:       {args.removed}")
    if cache_path:
        print(f"Cache:               {cache_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
