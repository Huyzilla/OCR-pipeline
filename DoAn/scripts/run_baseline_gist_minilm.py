from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from _bootstrap import setup_paths

setup_paths()

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable=None, **_kwargs):
        return iterable if iterable is not None else []

from baseline_fusion.outputs import build_debug_entry, open_output_csv, write_output_row
from baseline_fusion.runner import (
    build_pipeline_items,
    generate_answer_by_intent,
    load_resume_state,
    prepare_item,
    print_dry_run,
)
from qa.answer_utils import parse_answer
from qa.openai_client import init_client, load_env_file
from qa.output_io import save_json_list
from qa.question_io import load_questions
from qa.utils import detect_public_doc_ids


DATA_DIR = Path("data")
CACHE_DIR = Path("cache")
MODELS_DIR = Path("models")

MAX_QUESTIONS = 0
RESUME = True
DRY_RUN = False
LOAD_ENV_FILE = True
ENV_FILE = Path(".env")

QUESTION_FILE = DATA_DIR / "question.json"
CHUNK_DIR = Path("chunk_outputs1_finals")

OUTPUT_CSV = Path("baseline_gist_mnr_512d_minilm_h384_pruned_sbert_router.csv")
OUTPUT_JSON = Path("baseline_gist_mnr_512d_minilm_h384_pruned_sbert_router_debug.json")

QUERY_CACHE = CACHE_DIR / "cache_query_embeddings_question_json_embed_gist_mnr_512d.pkl"
PREPARED_CACHE = CACHE_DIR / "cache_prepared_question_json_embed_gist_mnr_512d_minilm_h384_pruned.pkl"
CHUNK_EMB_CACHE = CACHE_DIR / "cache_chunk_embeddings_embed_gist_mnr_512d_chunks1.pkl"
CHROMA_PATH = Path("chroma_db_viettel_embed_gist_mnr_512d_chunks1")
CHROMA_COLLECTION = "rag"

EMBEDDING_MODEL = str(MODELS_DIR / "embed_gist_mnr")
EMBEDDING_TRUNCATE_DIM = 512
RERANK_MODEL = str(MODELS_DIR / "MiniLM_H384_pruned_ft")
GPT_MODEL = "gpt-4o-mini"
ROUTER_MODEL = MODELS_DIR / "sbert_routing"

DENSE_TOP_K = 10
BM25_TOP_K = 10
FINAL_TOP_K = 5
PUB_DOC_TOP_K = 10


class SbertIntentRouter:
    def __init__(self, model_path: Path):
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"SBERT router not found: {model_path}")

        try:
            import joblib
            from sentence_transformers import SentenceTransformer
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "SBERT router requires sentence-transformers, joblib, scikit-learn, and torch. "
                "Install the project requirements in this Python environment first."
            ) from exc

        config_path = model_path / "intent_config.json"
        if config_path.exists():
            config = json.loads(config_path.read_text(encoding="utf-8"))
        else:
            config = {}

        self.labels = list(config.get("labels") or ["tra_cuu", "tinh_toan"])
        self.normalize_embeddings = bool(config.get("normalize_embeddings", True))
        self.segment = bool(config.get("segment", False))
        self.segment_text = None
        if self.segment:
            try:
                from pyvi.ViTokenizer import tokenize
            except ModuleNotFoundError as exc:
                raise RuntimeError(
                    "SBERT router is configured with segment=true, so pyvi is required."
                ) from exc
            self.segment_text = tokenize

        self._tmpdir = None
        load_path = self._compatible_model_path(model_path)
        self.encoder = SentenceTransformer(str(load_path))
        self.head = joblib.load(model_path / "head.joblib")

    def _compatible_model_path(self, model_path: Path) -> Path:
        modules_path = model_path / "modules.json"
        if not modules_path.exists():
            return model_path

        modules = json.loads(modules_path.read_text(encoding="utf-8"))
        replacements = {
            "sentence_transformers.base.modules.transformer.Transformer": "sentence_transformers.models.Transformer",
            "sentence_transformers.sentence_transformer.modules.pooling.Pooling": "sentence_transformers.models.Pooling",
        }
        patched = False
        for item in modules:
            module_type = item.get("type")
            if module_type in replacements:
                item["type"] = replacements[module_type]
                patched = True

        if not patched:
            return model_path

        self._tmpdir = TemporaryDirectory(prefix="sbert_router_")
        patched_path = Path(self._tmpdir.name) / model_path.name
        shutil.copytree(model_path, patched_path)
        (patched_path / "modules.json").write_text(
            json.dumps(modules, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        sentence_bert_config = patched_path / "sentence_bert_config.json"
        if sentence_bert_config.exists():
            sentence_bert_config.write_text(
                json.dumps({"max_seq_length": 256}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        tokenizer_config = patched_path / "tokenizer_config.json"
        if tokenizer_config.exists():
            tokenizer_data = json.loads(tokenizer_config.read_text(encoding="utf-8"))
            if isinstance(tokenizer_data.get("extra_special_tokens"), list):
                tokenizer_data["extra_special_tokens"] = {}
                tokenizer_config.write_text(
                    json.dumps(tokenizer_data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        pooling_config = patched_path / "1_Pooling" / "config.json"
        if pooling_config.exists():
            pooling_data = json.loads(pooling_config.read_text(encoding="utf-8"))
            if "embedding_dimension" in pooling_data and "word_embedding_dimension" not in pooling_data:
                pooling_data["word_embedding_dimension"] = pooling_data.pop("embedding_dimension")
                pooling_config.write_text(
                    json.dumps(pooling_data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        return patched_path

    def _label_from_prediction(self, prediction) -> str:
        if hasattr(prediction, "item"):
            prediction = prediction.item()
        if isinstance(prediction, bytes):
            prediction = prediction.decode("utf-8")
        if isinstance(prediction, str):
            if prediction in self.labels:
                return prediction
            text = prediction.strip().lower()
            if text in self.labels:
                return text
        try:
            idx = int(prediction)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Unknown SBERT router prediction: {prediction!r}") from exc
        if 0 <= idx < len(self.labels):
            return self.labels[idx]
        raise ValueError(f"SBERT router class index out of range: {idx}")

    def route(self, q_item: dict) -> tuple[str, list[str], float]:
        t0 = time.perf_counter()
        question = q_item["question"]
        encoded_question = self.segment_text(question) if self.segment_text else question
        embedding = self.encoder.encode(
            [encoded_question],
            normalize_embeddings=self.normalize_embeddings,
            show_progress_bar=False,
        )
        prediction = self.head.predict(embedding)[0]
        intent = self._label_from_prediction(prediction)
        route_s = time.perf_counter() - t0
        return intent, detect_public_doc_ids(question), route_s


def run_generation_loop(args, client, router, pipeline_items, retrieval_state, baseline_log) -> int:
    out_f, writer = open_output_csv(args.output_csv, args.resume)
    questions_run = 0

    try:
        for item in tqdm(pipeline_items, desc="Baseline"):
            q_seed = item["q_item"] if args.use_prepared_cache else item
            intent, router_public_ids, route_s = router.route(q_seed)
            prep = prepare_item(item, retrieval_state, args)
            q_item = prep["q_item"]
            prep["intent"] = intent
            prep["route_s"] = route_s
            prep["router_public_ids"] = router_public_ids

            t0 = time.perf_counter()
            raw, answer_s, reasoning, reasoning_s = generate_answer_by_intent(
                client, q_item, prep["context"], intent, args
            )
            num, predicted, format_ok = parse_answer(raw)
            generation_s = time.perf_counter() - t0

            write_output_row(
                writer, prep, raw, predicted, format_ok, answer_s, generation_s,
                intent=intent, route_s=route_s, reasoning_s=reasoning_s,
            )
            out_f.flush()
            baseline_log.append(build_debug_entry(
                "Baseline", prep, raw, num, predicted, format_ok, answer_s, generation_s,
                intent=intent, route_s=route_s,
                reasoning=reasoning, reasoning_s=reasoning_s,
            ))
            save_json_list(args.output_json, baseline_log)

            questions_run += 1
            tqdm.write(f"Q{q_item['index'] + 1}: intent={intent} baseline={predicted}")
    finally:
        out_f.close()

    return questions_run


def build_settings():
    return SimpleNamespace(
        question_csv=QUESTION_FILE,
        output_csv=OUTPUT_CSV,
        output_json=OUTPUT_JSON,
        fusion_csv=Path("unused_fusion_gist_mnr_minilm_h384_pruned.csv"),
        fusion_json=Path("unused_fusion_gist_mnr_minilm_h384_pruned_debug.json"),
        query_cache=QUERY_CACHE,
        prepared_cache=PREPARED_CACHE,
        use_prepared_cache=False,
        chunk_emb_cache=CHUNK_EMB_CACHE,
        chunk_dir=CHUNK_DIR,
        chroma_path=CHROMA_PATH,
        chroma_collection=CHROMA_COLLECTION,
        embedding_model=EMBEDDING_MODEL,
        embedding_truncate_dim=EMBEDDING_TRUNCATE_DIM,
        rerank_model=RERANK_MODEL,
        gpt_model=GPT_MODEL,
        router_model=ROUTER_MODEL,
        dense_top_k=DENSE_TOP_K,
        bm25_top_k=BM25_TOP_K,
        final_top_k=FINAL_TOP_K,
        pub_doc_top_k=PUB_DOC_TOP_K,
        n=MAX_QUESTIONS,
        resume=RESUME,
        fusion=False,
        env_file=ENV_FILE,
        load_env_file=LOAD_ENV_FILE,
        dry_run=DRY_RUN,
    )


def main() -> int:
    args = build_settings()

    if args.dry_run:
        print_dry_run(args)
        return 0

    if args.load_env_file:
        load_env_file(args.env_file, override=True)
    client = init_client()

    router = SbertIntentRouter(args.router_model)

    questions = load_questions(args.question_csv)
    if args.n > 0:
        questions = questions[: args.n]

    done_indices, baseline_log, fusion_log = load_resume_state(args)
    questions_to_run = [q for q in questions if q["index"] + 1 not in done_indices]

    if not questions_to_run:
        print("All questions already completed.")
        return 0

    t_all = time.perf_counter()
    pipeline_items, retrieval_state = build_pipeline_items(args, questions_to_run)
    questions_run = run_generation_loop(args, client, router, pipeline_items, retrieval_state, baseline_log)

    elapsed = time.perf_counter() - t_all
    print("\nDONE")
    print(f"Questions run:   {questions_run}")
    print(f"Baseline CSV:    {args.output_csv}")
    print(f"Baseline JSON:   {args.output_json}")
    print(f"Wall time:       {elapsed:.1f}s ({elapsed / 60:.1f} min)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
