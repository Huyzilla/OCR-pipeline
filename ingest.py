from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import chromadb

from chunking import process_document

# LlamaIndex imports hay thay doi theo version, nen dung fallback de de chay hon.
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.core.schema import NodeRelationship, RelatedNodeInfo, TextNode

try:
    from llama_index.core.storage.docstore import SimpleDocumentStore
except Exception:  # pragma: no cover
    from llama_index.core.storage.docstore.simple_docstore import SimpleDocumentStore

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.chroma import ChromaVectorStore


def default_chunk_config() -> dict[str, Any]:
    return {
        "text": {
            "chunk_size": 1200,
            "overlap": 300,
            "separators": ["\n\n", "\n", ". ", "; ", ": ", ") ", ", ", " "],
            "drop_too_short_chunk_size": 120,
        },
        "table": {
            "row_window": 10,
            "row_overlap": 2,
            "max_chunk_chars": 1800,
        },
    }


def chunks_to_nodes(custom_chunks: list[dict]) -> list[TextNode]:
    """Parse custom chunks thanh TextNode va gan quan he PREVIOUS/NEXT."""
    nodes: list[TextNode] = []

    for i, chunk in enumerate(custom_chunks):
        metadata = chunk.get("metadata", {}) or {}
        text = str(chunk.get("page_content", ""))

        chunk_id = metadata.get("chunk_id") or f"chunk::{i}"
        node = TextNode(
            id_=str(chunk_id),
            text=text,
            metadata=dict(metadata),
        )
        nodes.append(node)

    # Gan lien ket lan can dua tren metadata co san.
    for node in nodes:
        prev_chunk_id = node.metadata.get("prev_chunk_id")
        next_chunk_id = node.metadata.get("next_chunk_id")

        if prev_chunk_id:
            node.relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(node_id=str(prev_chunk_id))
        if next_chunk_id:
            node.relationships[NodeRelationship.NEXT] = RelatedNodeInfo(node_id=str(next_chunk_id))

    return nodes


def load_chunk_file(chunk_json_path: Path) -> list[dict]:
    with chunk_json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Chunk file khong hop le: {chunk_json_path}")

    return data


def build_nodes_from_markdown(md_path: Path, chunk_config: dict[str, Any]) -> list[TextNode]:
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    doc_id = md_path.stem
    custom_chunks = process_document(text=text, doc_id=doc_id, config=chunk_config)
    return chunks_to_nodes(custom_chunks)


def build_nodes_from_chunk_json(chunk_json_path: Path) -> list[TextNode]:
    custom_chunks = load_chunk_file(chunk_json_path)
    return chunks_to_nodes(custom_chunks)


def persist_pipeline(
    nodes: list[TextNode],
    chroma_dir: Path,
    chroma_collection: str,
    storage_dir: Path,
    bm25_dir: Path,
    embedding_model: str,
) -> None:
    # 1) Cau hinh embedding local HuggingFace
    Settings.embed_model = HuggingFaceEmbedding(model_name=embedding_model)

    # 2) Khoi tao Chroma local persistence
    chroma_client = chromadb.PersistentClient(path=str(chroma_dir))
    collection = chroma_client.get_or_create_collection(chroma_collection)
    vector_store = ChromaVectorStore(chroma_collection=collection)

    # 3) Khoi tao docstore de luu node raw (ho tro BM25 + prev/next retrieval)
    docstore = SimpleDocumentStore()
    storage_context = StorageContext.from_defaults(vector_store=vector_store, docstore=docstore)

    # 4) Add node vao docstore
    storage_context.docstore.add_documents(nodes)

    # 5) Index dense vector vao Chroma
    _ = VectorStoreIndex(nodes=nodes, storage_context=storage_context, embed_model=Settings.embed_model)

    # 6) Build sparse index BM25 va persist local
    bm25_dir.mkdir(parents=True, exist_ok=True)
    bm25_nodes_path = bm25_dir / "nodes.json"
    with bm25_nodes_path.open("w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "node_id": node.node_id,
                    "text": node.text,
                    "metadata": node.metadata,
                    "relationships": {
                        str(key): value.node_id if value else None
                        for key, value in node.relationships.items()
                    },
                }
                for node in nodes
            ],
            f,
            ensure_ascii=False,
            indent=2,
        )

    _bm25_retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=15)
    # Luu them manifest de query co the tai dung corpus khi can.
    with (bm25_dir / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump({"size": len(nodes), "files": {"nodes": "nodes.json"}}, f, ensure_ascii=False, indent=2)

    # 7) Persist toan bo storage context
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_context.persist(persist_dir=str(storage_dir))


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest: chunk -> node -> dense+sparse index")

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--input_md", help="Duong dan 1 file markdown OCR")
    source_group.add_argument("--input_chunk_json", help="Duong dan 1 file chunk JSON")
    source_group.add_argument("--input_dir", help="Thu muc chua nhieu file *_chunks.json")

    parser.add_argument("--config", default=None, help="Chunk config JSON (chi dung voi --input_md)")
    parser.add_argument("--chroma_dir", default="./chroma_db", help="Thu muc Chroma persistence")
    parser.add_argument("--chroma_collection", default="ocr_chunks", help="Ten collection trong Chroma")
    parser.add_argument("--storage_dir", default="./storage", help="Thu muc persist StorageContext")
    parser.add_argument("--bm25_dir", default="./bm25_store", help="Thu muc persist BM25Retriever")
    parser.add_argument(
        "--embedding_model",
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        help="HuggingFace embedding model local",
    )

    args = parser.parse_args()

    if args.input_md:
        input_md = Path(args.input_md)
        if not input_md.exists():
            raise FileNotFoundError(f"Khong tim thay file markdown: {input_md}")

        chunk_config = default_chunk_config()
        if args.config:
            config_path = Path(args.config)
            if not config_path.exists():
                raise FileNotFoundError(f"Khong tim thay config: {config_path}")
            chunk_config = json.loads(config_path.read_text(encoding="utf-8"))

        nodes = build_nodes_from_markdown(input_md, chunk_config)
    elif args.input_dir:
        input_dir = Path(args.input_dir)
        if not input_dir.exists():
            raise FileNotFoundError(f"Khong tim thay thu muc: {input_dir}")

        custom_chunks = load_chunks_from_dir(input_dir)
        nodes = chunks_to_nodes(custom_chunks)
    else:
        input_chunk_json = Path(args.input_chunk_json)
        if not input_chunk_json.exists():
            raise FileNotFoundError(f"Khong tim thay chunk json: {input_chunk_json}")
        nodes = build_nodes_from_chunk_json(input_chunk_json)

    persist_pipeline(
        nodes=nodes,
        chroma_dir=Path(args.chroma_dir),
        chroma_collection=args.chroma_collection,
        storage_dir=Path(args.storage_dir),
        bm25_dir=Path(args.bm25_dir),
        embedding_model=args.embedding_model,
    )

    print("Ingest thanh cong")
    print(f"- Nodes: {len(nodes)}")
    print(f"- Chroma dir: {args.chroma_dir}")
    print(f"- Storage dir: {args.storage_dir}")
    print(f"- BM25 dir: {args.bm25_dir}")


if __name__ == "__main__":
    main()
