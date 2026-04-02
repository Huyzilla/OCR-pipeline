from __future__ import annotations

import argparse
import json
import pickle
import re
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


def _tokenize_unicode_words(text: str) -> list[str]:
    """Simple tokenizer used for sparse BM25 indexing."""
    return re.findall(r"\w+", text.lower(), flags=re.UNICODE)


def _normalize_l2(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-12, None)
    return matrix / norms


def _flatten_chunk(chunk: dict) -> dict:
    page_content = chunk.get("page_content", "")
    metadata = chunk.get("metadata", {}) or {}

    flat = {
        "chunk_id": metadata.get("chunk_id"),
        "chunk_index": metadata.get("chunk_index"),
        "doc_id": metadata.get("doc_id"),
        "chunk_type": metadata.get("chunk_type"),
        "parent_id": metadata.get("parent_id"),
        "section_hint": metadata.get("section_hint"),
        "page_content": page_content,
    }

    # Keep extra metadata fields if they exist.
    for key, value in metadata.items():
        if key not in flat:
            flat[key] = value

    return flat


def _load_chunks(chunk_json_path: Path) -> list[dict]:
    with chunk_json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"File {chunk_json_path} khong co dinh dang list chunks")

    flattened = [_flatten_chunk(item) for item in data if isinstance(item, dict)]
    if not flattened:
        raise ValueError(f"File {chunk_json_path} khong co chunk hop le")

    return flattened


def build_dense_index(
    chunks: list[dict],
    dense_dir: Path,
    model_name: str,
    model: SentenceTransformer | None = None,
) -> None:
    dense_dir.mkdir(parents=True, exist_ok=True)

    texts = [str(c.get("page_content", "")) for c in chunks]
    if model is None:
        model = SentenceTransformer(model_name)

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True,
        normalize_embeddings=False,
    ).astype(np.float32)

    embeddings = _normalize_l2(embeddings)

    np.save(dense_dir / "embeddings.npy", embeddings)

    with (dense_dir / "chunk_map.json").open("w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    manifest = {
        "size": len(chunks),
        "dim": int(embeddings.shape[1]),
        "model_name": model_name,
        "normalized": True,
        "files": {
            "embeddings": "embeddings.npy",
            "chunk_map": "chunk_map.json",
        },
    }
    with (dense_dir / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def build_sparse_index(chunks: list[dict], sparse_dir: Path) -> None:
    sparse_dir.mkdir(parents=True, exist_ok=True)

    tokenized_corpus = [_tokenize_unicode_words(str(c.get("page_content", ""))) for c in chunks]
    bm25 = BM25Okapi(tokenized_corpus)

    with (sparse_dir / "bm25.pkl").open("wb") as f:
        pickle.dump(bm25, f)

    with (sparse_dir / "chunk_map.json").open("w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    manifest = {
        "size": len(chunks),
        "tokenizer": "regex_unicode_word",
        "files": {
            "bm25": "bm25.pkl",
            "chunk_map": "chunk_map.json",
        },
    }
    with (sparse_dir / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def infer_index_name(chunk_json_path: Path, input_root: Path | None) -> str:
    if input_root:
        rel = chunk_json_path.relative_to(input_root)
        if rel.parent != Path("."):
            return rel.parent.as_posix().replace("/", "_")
    return chunk_json_path.stem.replace("_chunks", "")


def index_one_file(
    chunk_json_path: Path,
    output_root: Path,
    model_name: str,
    input_root: Path | None = None,
    model: SentenceTransformer | None = None,
) -> Path:
    chunks = _load_chunks(chunk_json_path)
    index_name = infer_index_name(chunk_json_path, input_root)
    index_dir = output_root / index_name

    dense_dir = index_dir / "dense"
    sparse_dir = index_dir / "sparse"

    print(f"\nDang indexing: {chunk_json_path}")
    print(f"Output index : {index_dir}")
    print(f"Tong chunks  : {len(chunks)}")

    build_dense_index(chunks, dense_dir, model_name, model=model)
    build_sparse_index(chunks, sparse_dir)

    print("OK: Da tao dense + sparse index")
    return index_dir


def index_folder(input_dir: Path, output_root: Path, model_name: str) -> None:
    chunk_files = sorted(input_dir.rglob("*_chunks.json"))
    if not chunk_files:
        raise FileNotFoundError(f"Khong tim thay *_chunks.json trong: {input_dir}")

    success = 0
    failed = 0
    # Load model 1 lan cho toan bo batch de giam thoi gian indexing.
    model = SentenceTransformer(model_name)

    print(f"Tim thay {len(chunk_files)} file chunk json")
    for i, chunk_file in enumerate(chunk_files, 1):
        print(f"\n[{i}/{len(chunk_files)}]")
        try:
            index_one_file(
                chunk_json_path=chunk_file,
                output_root=output_root,
                model_name=model_name,
                input_root=input_dir,
                model=model,
            )
            success += 1
        except Exception as exc:
            print(f"FAIL: {exc}")
            failed += 1

    print("\n=== INDEXING SUMMARY ===")
    print(f"Thanh cong: {success}")
    print(f"That bai  : {failed}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build dense+sparse index tu chunk JSON")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input_json", help="Duong dan 1 file *_chunks.json")
    group.add_argument("--input_dir", help="Thu muc chua cac file *_chunks.json")

    parser.add_argument(
        "--output_dir",
        default="indexes",
        help="Thu muc output indexes (mac dinh: indexes)",
    )
    parser.add_argument(
        "--dense_model",
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        help="Ten sentence-transformers model cho dense embedding",
    )

    args = parser.parse_args()

    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    if args.input_json:
        input_json = Path(args.input_json)
        if not input_json.exists():
            raise FileNotFoundError(f"Khong tim thay file: {input_json}")
        index_one_file(
            chunk_json_path=input_json,
            output_root=output_root,
            model_name=args.dense_model,
            input_root=None,
        )
    else:
        input_dir = Path(args.input_dir)
        if not input_dir.exists():
            raise FileNotFoundError(f"Khong tim thay thu muc: {input_dir}")
        index_folder(input_dir=input_dir, output_root=output_root, model_name=args.dense_model)


if __name__ == "__main__":
    main()
