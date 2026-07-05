import argparse
import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

DEFAULT_DATA_DIR = Path("chunk_outputs_final_viettel")
DEFAULT_CHROMA_DB_PATH = "./chroma_db"
DEFAULT_COLLECTION_NAME = "rag"
DEFAULT_BATCH_SIZE = 256
DEFAULT_MODEL = "AITeamVN/Vietnamese_Embedding_v2"


def _sanitize_metadata(meta: dict) -> dict:
    safe = dict(meta) if meta else {}

    # Chroma does not accept list/dict metadata values.
    if "column_headers" in safe and isinstance(safe["column_headers"], list):
        safe["column_headers"] = " | ".join(safe["column_headers"])

    for key, value in list(safe.items()):
        if isinstance(value, (list, dict)):
            safe[key] = json.dumps(value, ensure_ascii=False)

    if not safe:
        safe["_source"] = "chunk"

    return safe


def main() -> None:
    parser = argparse.ArgumentParser(description="Index chunk JSON into ChromaDB")
    parser.add_argument("--data_dir", default=str(DEFAULT_DATA_DIR), help="Folder chứa các file chunk JSON")
    parser.add_argument("--chroma_path", default=DEFAULT_CHROMA_DB_PATH, help="Đường dẫn ChromaDB persistent")
    parser.add_argument("--collection_name", default=DEFAULT_COLLECTION_NAME, help="Tên collection ChromaDB")
    parser.add_argument("--batch_size", type=int, default=DEFAULT_BATCH_SIZE, help="Batch size khi indexing")
    parser.add_argument("--id_prefix", default="viettel_v1", help="Prefix để tránh đụng ID giữa các corpus")
    parser.add_argument("--reset_collection", action="store_true", help="Xóa collection cũ trước khi index")
    parser.add_argument("--smoke_query", default="chữ ký số", help="Câu query test sau khi index")
    parser.add_argument("--smoke_top_k", type=int, default=3, help="Số kết quả trả về cho smoke test")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        raise FileNotFoundError(f"Không tìm thấy data_dir: {data_dir}")

    print("Đang tải model Embedding...")
    embedding_model = SentenceTransformer(DEFAULT_MODEL)

    print("Khởi tạo ChromaDB...")
    chroma_client = chromadb.PersistentClient(path=args.chroma_path)

    if args.reset_collection:
        try:
            chroma_client.delete_collection(name=args.collection_name)
            print(f"Đã xóa collection cũ: {args.collection_name}")
        except Exception:
            pass

    collection = chroma_client.get_or_create_collection(name=args.collection_name)

    print(f"Đang quét các file JSON trong thư mục {data_dir}...")
    all_chunks = []
    for json_path in data_dir.rglob("*.json"):
        with open(json_path, "r", encoding="utf-8") as f:
            try:
                file_chunks = json.load(f)
                if isinstance(file_chunks, list):
                    all_chunks.extend(file_chunks)
            except Exception as exc:
                print(f"Lỗi khi đọc file {json_path}: {exc}")

    print(f"Có {len(all_chunks)} chunks.")
    if not all_chunks:
        return

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
        ids.append(f"{args.id_prefix}_{doc_id}_{c_type}_{c_idx}")

    print("Bắt đầu Indexing ...")
    for i in tqdm(range(0, len(documents), args.batch_size), desc="Indexing"):
        batch_docs = documents[i : i + args.batch_size]
        batch_metas = metadatas[i : i + args.batch_size]
        batch_ids = ids[i : i + args.batch_size]

        batch_embs = embedding_model.encode(batch_docs).tolist()
        collection.upsert(
            ids=batch_ids,
            embeddings=batch_embs,
            documents=batch_docs,
            metadatas=batch_metas,
        )

    print("Indexing xong!")

if __name__ == "__main__":
    main()