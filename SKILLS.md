# Coding Rules For This Repo

Use this file as the first context before making code changes in this repository.

## Senior-dev style

- Prefer simple, direct code over clever abstractions.
- Do not add classes, dataclasses, registries, factories, or generic frameworks unless the code clearly needs them.
- Keep the main path easy to read from top to bottom.
- A good function name is better than a comment explaining a confusing abstraction.
- Make the default command useful immediately, for example `python file.py`.
- Keep optional CLI flags minimal and practical: `--dry-run`, `--n`, `--no-resume`, `--output`, `--input`.

## Repo workflow

- Read existing code before editing.
- Follow the current file/module style.
- Keep edits scoped to the user request.
- Do not rewrite unrelated files.
- Do not move data/output paths unless the user asks.
- Prefer constants for fixed project paths and models.
- Prefer small helper functions over shared framework-style plumbing.

## Pipeline code

- Each pipeline stage should be a plain function with clear inputs and outputs.
- Stage wrappers should be runnable directly with no required arguments.
- Keep orchestration code separate from business logic.
- Put prompts near the GPT code that uses them.
- Use absolute paths internally when launching subprocesses.
- Run subprocesses from the repo root so relative data paths stay stable.
- Print the exact command before running it.
- Support `--dry-run` for stage runners.

## Data scripts

- Preserve JSONL schemas unless intentionally migrating them.
- When filtering data, write both the filtered output and an audit file for removed records.
- Cache expensive GPT/model calls when reruns are likely.
- Keep index/query/chunk IDs in outputs so files can be mapped back later.
- Fail loudly on missing required inputs.

## Validation

- After changing code, run the smallest useful check:
  - `python -m compileall <folder>` for syntax.
  - `python file.py --dry-run` for runners.
  - A small `--n` smoke test for expensive stages.
- If a check cannot run because of network/API/GPU/env constraints, say exactly what blocked it.

## What to avoid

- Do not over-engineer.
- Do not create abstractions just because code repeats twice.
- Do not hide simple commands behind too many layers.
- Do not silently swallow model/API errors.
- Do not print secrets from `.env` or environment variables.
- Do not change training data outputs casually.
