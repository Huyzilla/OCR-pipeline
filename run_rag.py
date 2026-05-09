"""
Unified RAG pipeline: chunking → indexing into ChromaDB.
One command to go from markdown outputs to a searchable vector store.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from rag.main_chunking import load_config, build_chunker, process_one_file as chunk_one_file


DEFAULT_MODEL = "AITeamVN/Vietnamese_Embedding_v2"


def _output_json_for_md(input_dir: Path, output_dir: Path, md_path: Path) -> Path:
    rel = md_path.relative_to(input_dir)
    out_parent = rel.parent if str(rel.parent) != "." else Path(md_path.parent.name)
    return output_dir / out_parent / "main_chunks_viettel.json"


def _load_chunk_file(json_path: Path) -> list[dict]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def _is_md_newer(md_path: Path, json_path: Path) -> bool:
    if not json_path.exists():
        return True
    return md_path.stat().st_mtime > json_path.stat().st_mtime


def _sanitize_metadata(meta: dict) -> dict:
    safe = dict(meta) if meta else {}
    if "column_headers" in safe and isinstance(safe["column_headers"], list):
        safe["column_headers"] = " | ".join(safe["column_headers"])
    for key, value in list(safe.items()):
        if isinstance(value, (list, dict)):
            safe[key] = json.dumps(value, ensure_ascii=False)
    if not safe:
        safe["_source"] = "chunk"
    return safe


def run_chunking(
    input_dir: Path,
    output_dir: Path,
    config: dict,
) -> list[Path]:
    """Chunk new or changed main.md files, return list of regenerated JSON paths."""
    md_files = sorted(input_dir.rglob("main.md"))
    if not md_files:
        raise FileNotFoundError(f"Khong tim thay file main.md trong: {input_dir}")

    print(f"Tim thay {len(md_files)} file markdown")
    json_paths: list[Path] = []
    success = 0
    failed = 0

    for i, md in enumerate(md_files, 1):
        out = _output_json_for_md(input_dir, output_dir, md)
        doc_id = md.parent.name if md.parent.name else md.stem

        if not _is_md_newer(md, out):
            continue

        print(f"  [{i}/{len(md_files)}] Chunking: {md}")
        try:
            total, text_count, table_count = chunk_one_file(md, out, config, doc_id=doc_id)
            print(f"    OK -> {out} | Total: {total} | Text: {text_count} | Table: {table_count}")
            json_paths.append(out)
            success += 1
        except Exception as e:
            print(f"    FAIL: {e}")
            failed += 1

    print(f"\nChunking: {success} thanh cong, {failed} that bai")
    return json_paths


def run_indexing(
    chunk_json_paths: list[Path],
    chroma_path: str,
    collection_name: str,
    batch_size: int = 256,
    id_prefix: str = "viettel_v1",
    reset_collection: bool = False,
) -> None:
    """Index only the provided chunk JSONs into ChromaDB."""
    print("\nDang tai model Embedding...")
    embedding_model = SentenceTransformer(DEFAULT_MODEL)

    print("Khoi tao ChromaDB...")
    chroma_client = chromadb.PersistentClient(path=chroma_path)

    def create_collection() -> chromadb.api.models.Collection.Collection:
        if reset_collection:
            try:
                chroma_client.delete_collection(name=collection_name)
                print(f"Da xoa collection cu: {collection_name}")
            except Exception:
                pass
        return chroma_client.get_or_create_collection(name=collection_name)

    collection = create_collection()

    if not chunk_json_paths:
        print("Khong co file chunk nao moi hoac thay doi de index.")
        return

    print(f"Dang quet {len(chunk_json_paths)} file JSON moi/thay doi...")
    all_chunks = []
    for json_path in sorted(chunk_json_paths):
        try:
            file_chunks = _load_chunk_file(json_path)
            if isinstance(file_chunks, list):
                all_chunks.extend(file_chunks)
        except Exception as exc:
            print(f"Loi khi doc {json_path}: {exc}")

    print(f"Co {len(all_chunks)} chunks.")
    if not all_chunks:
        return

    changed_doc_ids = sorted(
        {
            str((chunk.get("metadata", {}) or {}).get("document_id", "doc"))
            for chunk in all_chunks
            if isinstance(chunk, dict)
        }
    )

    for doc_id in changed_doc_ids:
        try:
            collection.delete(where={"document_id": doc_id})
            print(f"Da xoa chunks cu cua document_id={doc_id}")
        except Exception as exc:
            print(f"Khong the xoa chunks cu cua {doc_id}: {exc}")

    documents = []
    metadatas = []
    ids = []

    for chunk in all_chunks:
        text = chunk.get("page_content", "")
        meta = _sanitize_metadata(chunk.get("metadata", {}))
        documents.append(text)
        metadatas.append(meta)
        doc_id = meta.get("document_id", "doc")
        c_type = meta.get("chunk_type", "chunk")
        c_idx = meta.get("chunk_index", meta.get("table_id", 0))
        ids.append(f"{id_prefix}_{doc_id}_{c_type}_{c_idx}")

    def upsert_all(target_collection) -> None:
        print("Bat dau Indexing...")
        for i in tqdm(range(0, len(documents), batch_size), desc="Indexing"):
            batch_docs = documents[i : i + batch_size]
            batch_metas = metadatas[i : i + batch_size]
            batch_ids = ids[i : i + batch_size]
            batch_embs = embedding_model.encode(batch_docs).tolist()
            target_collection.upsert(
                ids=batch_ids,
                embeddings=batch_embs,
                documents=batch_docs,
                metadatas=batch_metas,
            )

    try:
        upsert_all(collection)
    except Exception as exc:
        error_text = str(exc).lower()
        if "embedding" in error_text and "dimension" in error_text and "got" in error_text:
            print("Phat hien mismatch dimension embedding. Dang xoa collection cu va index lai...")
            chroma_client.delete_collection(name=collection_name)
            collection = chroma_client.get_or_create_collection(name=collection_name)
            upsert_all(collection)
        else:
            raise

    print("Indexing xong!")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RAG pipeline: chunking markdown -> indexing into ChromaDB"
    )
    parser.add_argument("--input_dir", default="outputs", help="Thu muc chua cac outputs markdown (default: outputs)")
    parser.add_argument("--chunk_dir", default="chunk_outputs_finals", help="Thu muc luu chunk JSON (default: chunk_outputs_finals)")
    parser.add_argument("--chroma_path", default="./chroma_db_viettel", help="Duong dan ChromaDB")
    parser.add_argument("--collection_name", default="rag", help="Ten collection ChromaDB")
    parser.add_argument("--batch_size", type=int, default=256, help="Batch size khi indexing")
    parser.add_argument("--id_prefix", default="viettel_v1", help="Prefix ID")
    parser.add_argument("--reset_collection", action="store_true", help="Xoa collection cu truoc khi index")
    parser.add_argument("--config", default=None, help="Config JSON cho chunking")
    parser.add_argument("--skip_chunking", action="store_true", help="Bo qua buoc chunking, chi index")
    parser.add_argument("--skip_indexing", action="store_true", help="Bo qua buoc indexing, chi chunking")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    chunk_dir = Path(args.chunk_dir)

    # --- Step 1: Chunking ---
    if not args.skip_chunking:
        if not input_dir.exists():
            raise FileNotFoundError(f"Khong tim thay thu muc: {input_dir}")
        print(f"{'='*60}")
        print("STEP 1: CHUNKING")
        print(f"{'='*60}")
        config = load_config(args.config)
        chunk_json_paths = run_chunking(input_dir, chunk_dir, config)
    else:
        chunk_json_paths = []

    # --- Step 2: Indexing ---
    if not args.skip_indexing:
        if not args.skip_chunking and not chunk_dir.exists():
            raise FileNotFoundError(f"Khong tim thay thu muc chunk: {chunk_dir}")
        print(f"\n{'='*60}")
        print("STEP 2: INDEXING")
        print(f"{'='*60}")
        if args.skip_chunking:
            chunk_json_paths = sorted(chunk_dir.rglob("*.json")) if chunk_dir.exists() else []
        run_indexing(
            chunk_json_paths=chunk_json_paths,
            chroma_path=args.chroma_path,
            collection_name=args.collection_name,
            batch_size=args.batch_size,
            id_prefix=args.id_prefix,
            reset_collection=args.reset_collection,
        )

    print(f"\n{'='*60}")
    print("RAG PIPELINE DONE!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
