from pathlib import Path
import json
import os
import sys
import ssl
import time
import certifi

os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "120")
os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "60")

from huggingface_hub import hf_hub_download

sys.stdout.reconfigure(encoding="utf-8")


def find_repo_root(start: Path) -> Path:
    for path in (start, *start.parents):
        if (path / ".git").exists():
            return path
    return start

orig_ssl = ssl.create_default_context

def patched_ssl_context(*args, **kwargs):
    if not any(k in kwargs for k in ("cafile", "capath", "cadata")):
        kwargs["cafile"] = certifi.where()
    return orig_ssl(*args, **kwargs)

ssl.create_default_context = patched_ssl_context

REPO_ID = "unicamp-dl/mmarco"
BASE_DIR = find_repo_root(Path(__file__).resolve())
CACHE_DIR = BASE_DIR / "models" / "hf_cache" / "mmarco"
OUT_PATH = BASE_DIR / "data" / "mmarco_vi_100k.jsonl"
N = 100_000
MAX_DOWNLOAD_ATTEMPTS = 20
RETRY_SLEEP_SECONDS = 30

CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

files = {
    "collection": "data/google/collections/vietnamese_collection.tsv",
    "queries": "data/google/queries/train/vietnamese_queries.train.tsv",
    "triples": "data/triples.train.ids.small.tsv",
}

paths = {}

def download_with_retry(key, filename):
    for attempt in range(1, MAX_DOWNLOAD_ATTEMPTS + 1):
        try:
            print(
                f"Downloading {key}: {filename} "
                f"(attempt {attempt}/{MAX_DOWNLOAD_ATTEMPTS})",
                flush=True,
            )
            path = hf_hub_download(
                repo_id=REPO_ID,
                repo_type="dataset",
                filename=filename,
                cache_dir=str(CACHE_DIR),
                etag_timeout=60,
            )
            print(f"  -> {path}")
            return path
        except Exception as exc:
            if attempt == MAX_DOWNLOAD_ATTEMPTS:
                raise
            print(f"  Download failed: {type(exc).__name__}: {exc}")
            print(
                f"  Waiting {RETRY_SLEEP_SECONDS}s, then retrying. "
                "Existing partial download will be resumed when possible.",
                flush=True,
            )
            time.sleep(RETRY_SLEEP_SECONDS)


for key, filename in files.items():
    paths[key] = download_with_retry(key, filename)

print(f"Reading first {N} triples...")
triples = []
needed_qids = set()
needed_pids = set()

with open(paths["triples"], "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i >= N:
            break
        qid, pos_id, neg_id = line.rstrip("\n").split("\t")
        triples.append((qid, pos_id, neg_id))
        needed_qids.add(qid)
        needed_pids.add(pos_id)
        needed_pids.add(neg_id)

print(f"Needed queries: {len(needed_qids)}")
print(f"Needed passages: {len(needed_pids)}")

queries = {}
with open(paths["queries"], "r", encoding="utf-8") as f:
    for line in f:
        qid, text = line.rstrip("\n").split("\t", 1)
        if qid in needed_qids:
            queries[qid] = text

collection = {}
with open(paths["collection"], "r", encoding="utf-8") as f:
    for line in f:
        pid, text = line.rstrip("\n").split("\t", 1)
        if pid in needed_pids:
            collection[pid] = text
            if len(collection) == len(needed_pids):
                break

missing_q = needed_qids - queries.keys()
missing_p = needed_pids - collection.keys()

if missing_q or missing_p:
    raise RuntimeError(
        f"Missing queries={len(missing_q)}, missing passages={len(missing_p)}"
    )

print(f"Writing {OUT_PATH}")
with open(OUT_PATH, "w", encoding="utf-8") as out:
    for qid, pos_id, neg_id in triples:
        row = {
            "query": queries[qid],
            "positive": collection[pos_id],
            "negative": collection[neg_id],
            "query_id": qid,
            "positive_id": pos_id,
            "negative_id": neg_id,
        }
        out.write(json.dumps(row, ensure_ascii=False) + "\n")

print("Done.")
print(f"Output: {OUT_PATH}")
print(f"Rows: {len(triples)}")
