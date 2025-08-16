#!/usr/bin/env python3
import os
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from app.deps import get_supabase
from openai import OpenAI

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


def fetch_summaries(sb):
    res = sb.table("testimonies").select("id, summary").not_.is_("summary", None).execute().data
    return [r for r in res if isinstance(r.get("summary"), str) and r["summary"].strip()]


def fetch_existing_ids(sb):
    rows = sb.table("testimony_embeddings").select("testimony_id").execute().data
    return set(r["testimony_id"] for r in rows)


def embed_batch(client, texts):
    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [d.embedding for d in resp.data]


def upsert_embeddings(sb, pairs):
    payload = [{"testimony_id": tid, "embedding": emb} for tid, emb in pairs]
    try:
        sb.table("testimony_embeddings").upsert(payload, on_conflict="testimony_id").execute()
    except Exception as e:
        msg = str(e)
        print("ERROR during upsert: ", msg)
        if "42P10" in msg or "ON CONFLICT" in msg:
            print(
                "Hint: Create a unique index on testimony_id before running this script:\n"
                "  create unique index if not exists testimony_embeddings_unique on public.testimony_embeddings (testimony_id);\n"
            )
        raise


def run():
    sb = get_supabase()
    client = OpenAI()
    rows = fetch_summaries(sb)
    existing = fetch_existing_ids(sb)
    todo = [(r["id"], r["summary"].replace("\n", " ")) for r in rows if r["id"] not in existing]
    print(f"Embedding {len(todo)} testimonies with {EMBEDDING_MODEL}...")

    batch = 64
    for i in range(0, len(todo), batch):
        chunk = todo[i : i + batch]
        ids = [tid for tid, _ in chunk]
        texts = [t for _, t in chunk]
        vecs = embed_batch(client, texts)
        upsert_embeddings(sb, list(zip(ids, vecs)))
        print(f"Upserted {i + len(chunk)}/{len(todo)}")
        time.sleep(0.2)


if __name__ == "__main__":
    run()
