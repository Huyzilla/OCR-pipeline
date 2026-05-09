#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Summary Management Utility
Regenerate, update, inspect, and manage document summaries
"""

import json
import argparse
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load OPENAI_API_KEY từ .env
except ImportError:
    pass  # python-dotenv không cài thì bỏ qua, API key phải được export sẵn

from pipeline_router_summary.summary_generator import SummaryGenerator
from pipeline_router_summary.summary_indexer import SummaryIndexer, create_summary_indexer
from qa.utils import load_all_chunks, load_doc_chunks


def create_summary_generator(model_name: str = "gpt-4o-mini") -> SummaryGenerator:
    return SummaryGenerator(model_name)


def cmd_generate(
    chunk_dir: Path,
    output_json: Path,
    specific_docs: Optional[list] = None,
    md_dir: Path = Path("outputs")
):
    """Generate summaries"""
    print("="*70)
    print("Generate Summaries")
    print("="*70)
    
    generator = create_summary_generator("gpt-4o-mini")
    
    # Load documents
    print(f"\nLoading documents...")
    documents = {}
    
    if specific_docs:
        doc_dirs = [chunk_dir / doc_id for doc_id in specific_docs]
    else:
        doc_dirs = sorted(chunk_dir.glob("Public*"))
    
    for doc_path in doc_dirs:
        if doc_path.is_dir():
            doc_id = doc_path.name
            
            # Ưu tiên đọc file markdown gốc
            md_file = md_dir / doc_id / "main.md"
            if md_file.exists():
                documents[doc_id] = md_file.read_text(encoding="utf-8", errors="ignore")
            else:
                # Fallback: ghép chunks
                chunks = load_doc_chunks(chunk_dir, doc_id)
                if chunks:
                    documents[doc_id] = "\n\n".join([c.text for c in chunks])
    
    print(f"Loaded {len(documents)} documents (preferred .md if available)")
    
    if not documents:
        print("No documents found!")
        return
    
    # Generate
    summaries = generator.generate_summaries_batch(documents, output_json=output_json)
    print(f"✓ Generated {len(summaries)} summaries")


def cmd_rebuild_index(
    summaries_json: Path,
    chroma_path: Path
):
    """Rebuild ChromaDB index from JSON"""
    print("="*70)
    print("Rebuild ChromaDB Index")
    print("="*70)
    
    if not summaries_json.exists():
        print(f"Error: {summaries_json} not found!")
        return
    
    print(f"\nLoading summaries from {summaries_json}...")
    with open(summaries_json, 'r', encoding='utf-8') as f:
        summaries = json.load(f)
    
    print(f"Loaded {len(summaries)} summaries")
    
    # Create indexer
    indexer = create_summary_indexer(
        chroma_db_path=chroma_path,
        json_output_path=summaries_json
    )
    
    # Reset and rebuild
    print("Resetting ChromaDB...")
    indexer.reset_index()
    
    print("Indexing summaries...")
    indexer.add_summaries(summaries)
    
    print("✓ ChromaDB index rebuilt")


def cmd_inspect(
    summaries_json: Path,
    num_samples: int = 3
):
    """Inspect summaries"""
    print("="*70)
    print("Inspect Summaries")
    print("="*70)
    
    if not summaries_json.exists():
        print(f"Error: {summaries_json} not found!")
        return
    
    with open(summaries_json, 'r', encoding='utf-8') as f:
        summaries = json.load(f)
    
    print(f"\nTotal summaries: {len(summaries)}")
    
    # Stats
    total_tokens = sum(s.get('token_count', 0) for s in summaries)
    avg_tokens = total_tokens / len(summaries) if summaries else 0
    
    print(f"Average tokens per summary: {avg_tokens:.1f}")
    print(f"Total tokens: {total_tokens}")
    
    # Sample
    print(f"\nSample summaries (first {num_samples}):")
    for i, s in enumerate(summaries[:num_samples], 1):
        print(f"\n[{i}] Doc: {s['doc_id']}")
        print(f"    Chunks: {s['chunk_count']}")
        print(f"    Tokens: {s['token_count']}")
        print(f"    Summary: {s['summary_text'][:150]}...")
    
    # Distribution
    print(f"\nToken distribution:")
    token_ranges = [(0, 100), (100, 150), (150, 200), (200, 300), (300, float('inf'))]
    for start, end in token_ranges:
        count = sum(1 for s in summaries if start <= s.get('token_count', 0) < end)
        pct = count / len(summaries) * 100 if summaries else 0
        end_str = "inf" if end == float('inf') else str(int(end))
        print(f"  {start:3d}-{end_str:>3} tokens: {count:3d} ({pct:5.1f}%)")


def cmd_search(
    summaries_json: Path,
    chroma_path: Path,
    query: str,
    top_k: int = 5
):
    """Search summaries"""
    print("="*70)
    print(f"Search Summaries")
    print("="*70)
    
    indexer = create_summary_indexer(
        chroma_db_path=chroma_path,
        json_output_path=summaries_json
    )
    
    print(f"\nSearching for: {query}")
    results = indexer.search_summaries(query, top_k=top_k)
    
    print(f"\nTop {top_k} results:")
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r['doc_id']}")
        print(f"    Distance: {r['distance']:.4f}")
        print(f"    Chunks: {r['chunk_count']}")
        print(f"    Tokens: {r['token_count']}")
        print(f"    Summary: {r['summary_text'][:100]}...")


def cmd_stats(
    summaries_json: Path,
    chroma_path: Path
):
    """Show statistics"""
    print("="*70)
    print("Statistics")
    print("="*70)
    
    # JSON stats
    if summaries_json.exists():
        with open(summaries_json, 'r', encoding='utf-8') as f:
            summaries = json.load(f)
        
        print(f"\nJSON File: {summaries_json}")
        print(f"  Total docs: {len(summaries)}")
        print(f"  File size: {summaries_json.stat().st_size / 1024 / 1024:.2f} MB")
    
    # ChromaDB stats
    indexer = create_summary_indexer(chroma_path=chroma_path, json_output_path=summaries_json)
    stats = indexer.get_stats()
    
    print(f"\nChromaDB: {chroma_path}")
    for key, value in stats.items():
        if key != 'json_file':
            print(f"  {key}: {value}")


def cmd_export(
    summaries_json: Path,
    output_csv: Path
):
    """Export summaries to CSV"""
    print("="*70)
    print("Export Summaries to CSV")
    print("="*70)
    
    if not summaries_json.exists():
        print(f"Error: {summaries_json} not found!")
        return
    
    with open(summaries_json, 'r', encoding='utf-8') as f:
        summaries = json.load(f)
    
    import csv
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['doc_id', 'chunks', 'tokens', 'summary'])
        writer.writeheader()
        
        for s in summaries:
            writer.writerow({
                'doc_id': s['doc_id'],
                'chunks': s['chunk_count'],
                'tokens': s['token_count'],
                'summary': s['summary_text']
            })
    
    print(f"✓ Exported {len(summaries)} summaries to {output_csv}")


def main():
    parser = argparse.ArgumentParser(description="Summary Management Utility")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # generate
    gen_parser = subparsers.add_parser("generate", help="Generate summaries")
    gen_parser.add_argument("--chunk-dir", type=Path, default=Path("chunk_outputs_finals"))
    gen_parser.add_argument("--md-dir", type=Path, default=Path("outputs"), help="Directory containing raw markdown files")
    gen_parser.add_argument("--output", type=Path, default=Path("summaries.json"))
    gen_parser.add_argument("--docs", nargs="+", help="Specific docs to generate (e.g., Public001 Public002)")
    
    # rebuild
    rebuild_parser = subparsers.add_parser("rebuild", help="Rebuild ChromaDB index")
    rebuild_parser.add_argument("--summaries", type=Path, default=Path("summaries.json"))
    rebuild_parser.add_argument("--chroma", type=Path, default=Path("chroma_db_summaries"))
    
    # inspect
    inspect_parser = subparsers.add_parser("inspect", help="Inspect summaries")
    inspect_parser.add_argument("--summaries", type=Path, default=Path("summaries.json"))
    inspect_parser.add_argument("--samples", type=int, default=3)
    
    # search
    search_parser = subparsers.add_parser("search", help="Search summaries")
    search_parser.add_argument("query", help="Query text")
    search_parser.add_argument("--summaries", type=Path, default=Path("summaries.json"))
    search_parser.add_argument("--chroma", type=Path, default=Path("chroma_db_summaries"))
    search_parser.add_argument("--top-k", type=int, default=5)
    
    # stats
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.add_argument("--summaries", type=Path, default=Path("summaries.json"))
    stats_parser.add_argument("--chroma", type=Path, default=Path("chroma_db_summaries"))
    
    # export
    export_parser = subparsers.add_parser("export", help="Export to CSV")
    export_parser.add_argument("--summaries", type=Path, default=Path("summaries.json"))
    export_parser.add_argument("--output", type=Path, default=Path("summaries.csv"))
    
    args = parser.parse_args()
    
    if args.command == "generate":
        cmd_generate(args.chunk_dir, args.output, args.docs, getattr(args, "md_dir", Path("outputs")))
    elif args.command == "rebuild":
        cmd_rebuild_index(args.summaries, args.chroma)
    elif args.command == "inspect":
        cmd_inspect(args.summaries, args.samples)
    elif args.command == "search":
        cmd_search(args.summaries, args.chroma, args.query, args.top_k)
    elif args.command == "stats":
        cmd_stats(args.summaries, args.chroma)
    elif args.command == "export":
        cmd_export(args.summaries, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
