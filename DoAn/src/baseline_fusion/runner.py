from __future__ import annotations

import time

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable=None, **_kwargs):
        return iterable if iterable is not None else []

from baseline_fusion.prompts import (
    create_cot_answer_prompt,
    create_cot_reasoning_prompt,
    create_fusion_extract_prompt,
    create_standard_answer_prompt,
)
from baseline_fusion.retrieval import (
    load_prepared_cache,
    prepare_retrieval,
    retrieve_one,
    run_phase1,
    build_prepared_entry,
)
from qa.openai_client import call_gpt
from qa.output_io import (
    load_done_indices,
    load_json_list,
    trim_debug_log,
    trim_output_csv,
)
from qa.utils import detect_public_doc_ids


MAX_TOKENS = 16
COT_MAX_TOKENS = 400
FUSION_EXTRACT_MAX_TOKENS = 400
TEMPERATURE = 0
MAX_RETRIES = 5
RETRY_DELAY = 2
PHASE1_CHECKPOINT_EVERY = 1

ROUTER_PROMPT = """Phân loại intent của câu hỏi sau. Trả lời chỉ một từ:
- "tra_cuu" nếu câu hỏi yêu cầu tra cứu, tìm kiếm thông tin, định nghĩa, giải thích
- "tinh_toan" nếu câu hỏi yêu cầu tính toán, suy luận số liệu, so sánh theo phép tính

Câu hỏi: {question}

Intent:"""


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
    print(f"  question_file    : {args.question_csv}")
    print(f"  chunk_dir        : {args.chunk_dir}")
    print(f"  chroma_path      : {args.chroma_path}")
    print(f"  router_model     : {args.router_model}")
    print(f"  embedding_dim    : {getattr(args, 'embedding_truncate_dim', None) or 'default'}")
    print(f"  rerank_model     : {args.rerank_model}")
    print(f"  gpt_model        : {args.gpt_model}")
    print(f"  max_questions    : {args.n}")
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


def load_resume_state(args) -> tuple[set[int], list[dict], list[dict]]:
    done_indices = load_done_indices(args.output_csv) if args.resume else set()

    if args.resume and args.fusion:
        fusion_done_indices = load_done_indices(args.fusion_csv)
        if done_indices != fusion_done_indices:
            common_done_indices = done_indices & fusion_done_indices
            if not common_done_indices:
                raise SystemExit(
                    "Resume mismatch: baseline CSV and fusion CSV do not share "
                    "completed question_index values. Set RESUME = False to start "
                    "fresh, or choose different output files at the top of this file."
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


def parse_intent(raw: str) -> str:
    text = (raw or "").strip().lower()
    if "tinh_toan" in text or "tính toán" in text:
        return "tinh_toan"
    if "tra_cuu" in text or "tra cứu" in text:
        return "tra_cuu"
    return "tra_cuu"


def route_question(client, q_item: dict, args) -> tuple[str, list[str], float]:
    raw, route_s = call_gpt(
        client,
        ROUTER_PROMPT.format(question=q_item["question"]),
        model=args.router_model,
        max_tokens=16,
        temperature=TEMPERATURE,
        max_retries=MAX_RETRIES,
        retry_delay=RETRY_DELAY,
    )
    return parse_intent(raw), detect_public_doc_ids(q_item["question"]), route_s


def generate_answer_by_intent(
    client,
    q_item: dict,
    context: str,
    intent: str,
    args,
) -> tuple[str, float, str, float]:
    if intent == "tinh_toan":
        reasoning_prompt = create_cot_reasoning_prompt(
            q_item["question"], context, q_item["options"]
        )
        reasoning, reasoning_s = call_answer_gpt(
            client, reasoning_prompt, args, max_tokens=COT_MAX_TOKENS
        )
        answer_prompt = create_cot_answer_prompt(
            q_item["question"], reasoning, q_item["options"]
        )
        raw, answer_s = call_answer_gpt(client, answer_prompt, args)
        return raw, answer_s, reasoning, reasoning_s

    prompt = create_standard_answer_prompt(q_item["question"], context, q_item["options"])
    raw, answer_s = call_answer_gpt(client, prompt, args)
    return raw, answer_s, "", 0.0


def generate_fusion_context(client, q_item: dict, context: str, args) -> tuple[str, float]:
    extract_prompt = create_fusion_extract_prompt(q_item["question"], context)
    return call_answer_gpt(client, extract_prompt, args, max_tokens=FUSION_EXTRACT_MAX_TOKENS)
