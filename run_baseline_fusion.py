from __future__ import annotations

import argparse
import time
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable=None, **_kwargs):
        return iterable if iterable is not None else []

from baseline_fusion.outputs import build_debug_entry, open_output_csv, write_output_row
from baseline_fusion.prompts import create_answer_prompt, create_fusion_extract_prompt
from baseline_fusion.retrieval import (
    build_prepared_entry,
    load_prepared_cache,
    prepare_retrieval,
    retrieve_one,
    run_phase1,
)
from qa.answer_utils import parse_answer
from qa.openai_client import call_gpt, init_client, load_env_file
from qa.output_io import (
    load_done_indices,
    load_json_list,
    save_json_list,
    trim_debug_log,
    trim_output_csv,
)
from qa.question_io import load_questions


FUSION = False
USE_PREPARED_CACHE = False

DATA_DIR = Path("data")
CACHE_DIR = Path("cache")
QUESTION_CSV = DATA_DIR / "question.csv"
BASELINE_CSV = Path("baseline.csv")
BASELINE_JSON = Path("baseline_debug.json")
FUSION_CSV = Path("fusion.csv")
FUSION_JSON = Path("fusion_debug.json")

QUERY_CACHE = CACHE_DIR / "cache_query_embeddings.pkl"
PREPARED_CACHE = CACHE_DIR / "cache_prepared.pkl"
CHUNK_EMB_CACHE = CACHE_DIR / "cache_chunk_embeddings.pkl"
CHUNK_DIR = Path("chunk_outputs_finals")
CHROMA_PATH = Path("chroma_db_viettel")
CHROMA_COLLECTION = "rag"

EMBEDDING_MODEL = "AITeamVN/Vietnamese_Embedding_v2"
RERANK_MODEL = "stage_b_adrmse"
GPT_MODEL = "gpt-4o-mini"

DENSE_TOP_K = 10
BM25_TOP_K = 10
FINAL_TOP_K = 5
PUB_DOC_TOP_K = 10
MAX_TOKENS = 16
TEMPERATURE = 0
MAX_RETRIES = 5
RETRY_DELAY = 2
PHASE1_CHECKPOINT_EVERY = 1


def call_answer_gpt(client, prompt: str, args, max_tokens: int = MAX_TOKENS) -> tuple[str, float]:
    return call_gpt(
        client,
        prompt,
        model=args.gpt_model,
        max_tokens=max_tokens,
        temperature=TEMPERATURE,
        max_retries=MAX_RETRIES,
        retry_delay=RETRY_DELAY,
    )


def print_dry_run(args) -> None:
    print("Dry run configuration")
    print(f"  question_csv     : {args.question_csv}")
    print(f"  chunk_dir        : {args.chunk_dir}")
    print(f"  chroma_path      : {args.chroma_path}")
    print(f"  rerank_model     : {args.rerank_model}")
    print(f"  gpt_model        : {args.gpt_model}")
    print(f"  resume           : {args.resume}")
    print(f"  prepared_cache   : {args.use_prepared_cache}")
    print(f"  query_cache      : {args.query_cache}")
    print(f"  prepared_path    : {args.prepared_cache}")
    print(f"  chunk_emb_cache  : {args.chunk_emb_cache}")
    print(f"  fusion           : {args.fusion}")
    print(f"  baseline_csv     : {args.output_csv}")
    print(f"  baseline_json    : {args.output_json}")
    if args.fusion:
        print(f"  fusion_csv       : {args.fusion_csv}")
        print(f"  fusion_json      : {args.fusion_json}")


def parse_args():
    parser = argparse.ArgumentParser(description="Run baseline QA, optionally with fusion.")
    parser.add_argument("--question-csv", type=Path, default=QUESTION_CSV)
    parser.add_argument("--output-csv", type=Path, default=BASELINE_CSV)
    parser.add_argument("--output-json", type=Path, default=BASELINE_JSON)
    parser.add_argument("--fusion-csv", type=Path, default=FUSION_CSV)
    parser.add_argument("--fusion-json", type=Path, default=FUSION_JSON)
    parser.add_argument("--query-cache", type=Path, default=QUERY_CACHE)
    parser.add_argument("--prepared-cache", type=Path, default=PREPARED_CACHE)
    parser.add_argument("--use-prepared-cache", action="store_true", default=USE_PREPARED_CACHE)
    parser.add_argument("--chunk-emb-cache", type=Path, default=CHUNK_EMB_CACHE)
    parser.add_argument("--chunk-dir", type=Path, default=CHUNK_DIR)
    parser.add_argument("--chroma-path", type=Path, default=CHROMA_PATH)
    parser.add_argument("--chroma-collection", default=CHROMA_COLLECTION)
    parser.add_argument("--embedding-model", default=EMBEDDING_MODEL)
    parser.add_argument("--rerank-model", default=RERANK_MODEL)
    parser.add_argument("--gpt-model", default=GPT_MODEL)
    parser.add_argument("--dense-top-k", type=int, default=DENSE_TOP_K)
    parser.add_argument("--bm25-top-k", type=int, default=BM25_TOP_K)
    parser.add_argument("--final-top-k", type=int, default=FINAL_TOP_K)
    parser.add_argument("--pub-doc-top-k", type=int, default=PUB_DOC_TOP_K)
    parser.add_argument("--n", type=int, default=0)
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--fusion", action="store_true", default=FUSION)
    parser.add_argument("--no-fusion", action="store_false", dest="fusion")
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--no-env-file", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    args.resume = not args.no_resume
    return args


def load_resume_state(args) -> tuple[set[int], list[dict], list[dict]]:
    done_indices = load_done_indices(args.output_csv) if args.resume else set()

    if args.resume and args.fusion:
        fusion_done_indices = load_done_indices(args.fusion_csv)
        if done_indices != fusion_done_indices:
            common_done_indices = done_indices & fusion_done_indices
            if not common_done_indices:
                raise SystemExit(
                    "Resume mismatch: baseline CSV and fusion CSV do not share "
                    "completed question_index values. Use --no-resume to start "
                    "fresh, or choose different --output-csv/--fusion-csv files."
                )
            done_indices = common_done_indices
            print(
                "Resume mismatch: baseline CSV and fusion CSV have different "
                f"question_index sets. Keeping {len(done_indices)} completed pairs."
            )
            trim_output_csv(args.output_csv, done_indices)
            trim_output_csv(args.fusion_csv, done_indices)
            trim_debug_log(args.output_json, done_indices)
            trim_debug_log(args.fusion_json, done_indices)

    baseline_log = load_json_list(args.output_json) if args.resume else []
    fusion_log = load_json_list(args.fusion_json) if args.resume and args.fusion else []
    return done_indices, baseline_log, fusion_log


def build_pipeline_items(args, questions_to_run: list[dict]):
    if args.use_prepared_cache:
        expected_indices = [q["index"] for q in questions_to_run]
        prepared = load_prepared_cache(args.prepared_cache, expected_indices) if args.resume else None
        if prepared is None:
            prepared = run_phase1(
                questions_to_run,
                questions_to_run,
                args,
                checkpoint_every=PHASE1_CHECKPOINT_EVERY,
            )
        elif len(prepared) < len(questions_to_run):
            more = run_phase1(
                questions_to_run[len(prepared):],
                questions_to_run,
                args,
                existing=prepared,
                checkpoint_every=PHASE1_CHECKPOINT_EVERY,
            )
            prepared.extend(more)
        else:
            print("  Skipping Phase 1 (using cached results)")
        print(f"\nPhase 2: GPT answer generation ({len(prepared)} questions)")
        return prepared, None

    print(f"\nPipeline: retrieve + rerank + GPT ({len(questions_to_run)} questions)")
    retrieval_state = prepare_retrieval(args, questions_to_run)
    return questions_to_run, retrieval_state


def prepare_item(item: dict, retrieval_state, args) -> dict:
    if args.use_prepared_cache:
        return item

    top_chunks, meta = retrieve_one(item, retrieval_state, args)
    return build_prepared_entry(item, top_chunks, meta)


def run_generation_loop(args, client, pipeline_items, retrieval_state, baseline_log, fusion_log) -> int:
    out_f, writer = open_output_csv(args.output_csv, args.resume)
    if args.fusion:
        fusion_f, fusion_writer = open_output_csv(args.fusion_csv, args.resume)
    else:
        fusion_f = None
        fusion_writer = None

    questions_run = 0
    try:
        desc = "Baseline+Fusion" if args.fusion else "Baseline"
        for item in tqdm(pipeline_items, desc=desc):
            prep = prepare_item(item, retrieval_state, args)
            q_item = prep["q_item"]

            t0 = time.perf_counter()
            raw, answer_s = call_answer_gpt(client, prep["prompt"], args)
            num, predicted, format_ok = parse_answer(raw)
            generation_s = time.perf_counter() - t0

            msg = f"Q{q_item['index'] + 1}: baseline={predicted}"

            if args.fusion:
                t0 = time.perf_counter()
                extract_prompt = create_fusion_extract_prompt(q_item["question"], prep["context"])
                extracted, extract_s = call_answer_gpt(client, extract_prompt, args, max_tokens=400)
                fusion_prompt = create_answer_prompt(q_item["question"], extracted, q_item["options"])
                fu_raw, fu_answer_s = call_answer_gpt(client, fusion_prompt, args)
                fu_num, fu_predicted, fu_ok = parse_answer(fu_raw)
                fu_generation_s = time.perf_counter() - t0

                write_output_row(writer, prep, raw, predicted, format_ok, answer_s, generation_s)
                out_f.flush()
                baseline_log.append(build_debug_entry(
                    "Baseline", prep, raw, num, predicted, format_ok, answer_s, generation_s
                ))
                save_json_list(args.output_json, baseline_log)

                write_output_row(
                    fusion_writer, prep, fu_raw, fu_predicted, fu_ok,
                    fu_answer_s, fu_generation_s, extract_s=extract_s,
                )
                fusion_f.flush()
                fusion_log.append(build_debug_entry(
                    "Fusion", prep, fu_raw, fu_num, fu_predicted, fu_ok,
                    fu_answer_s, fu_generation_s, extracted=extracted, extract_s=extract_s,
                ))
                save_json_list(args.fusion_json, fusion_log)
                msg += f" | fusion={fu_predicted}"
            else:
                write_output_row(writer, prep, raw, predicted, format_ok, answer_s, generation_s)
                out_f.flush()
                baseline_log.append(build_debug_entry(
                    "Baseline", prep, raw, num, predicted, format_ok, answer_s, generation_s
                ))
                save_json_list(args.output_json, baseline_log)

            questions_run += 1
            tqdm.write(msg)
    finally:
        out_f.close()
        if fusion_f is not None:
            fusion_f.close()

    return questions_run


def main() -> int:
    args = parse_args()

    if args.dry_run:
        print_dry_run(args)
        return 0

    if not args.no_env_file:
        load_env_file(args.env_file, override=True)
    client = init_client()

    questions = load_questions(args.question_csv)
    if args.n > 0:
        questions = questions[:args.n]

    done_indices, baseline_log, fusion_log = load_resume_state(args)
    questions_to_run = [q for q in questions if q["index"] + 1 not in done_indices]

    if not questions_to_run:
        print("All questions already completed.")
        return 0

    t_all = time.perf_counter()
    pipeline_items, retrieval_state = build_pipeline_items(args, questions_to_run)
    questions_run = run_generation_loop(
        args, client, pipeline_items, retrieval_state, baseline_log, fusion_log
    )

    elapsed = time.perf_counter() - t_all
    print("\nDONE")
    print(f"Questions run:   {questions_run}")
    print(f"Baseline CSV:    {args.output_csv}")
    print(f"Baseline JSON:   {args.output_json}")
    if args.fusion:
        print(f"Fusion CSV:      {args.fusion_csv}")
        print(f"Fusion JSON:     {args.fusion_json}")
    print(f"Wall time:       {elapsed:.1f}s ({elapsed / 60:.1f} min)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
