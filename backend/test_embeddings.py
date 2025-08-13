#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from typing import List, Tuple

import numpy as np
from openai import OpenAI

# Allow importing app.deps to use Supabase client
sys.path.append(str(Path(__file__).parent / "src"))
try:
    from app.deps import get_supabase
except Exception:
    get_supabase = None  # Optional for file-only mode


DEFAULT_SAMPLES = Path(__file__).parent / "temp_summaries.txt"
MODELS = [
    ("text-embedding-3-small", 1536),
    ("text-embedding-3-large", 3072),
]


def read_blocks(path: Path) -> List[str]:
    txt = path.read_text(encoding="utf-8")
    blocks = [b.strip() for b in txt.split("\n") if b.strip()]
    return [b.replace("\n", " ") for b in blocks]


def fetch_summaries_from_supabase(limit: int = 350) -> List[str]:
    if get_supabase is None:
        raise RuntimeError("Supabase client not available. Ensure backend/src is on sys.path.")
    sb = get_supabase()
    res = sb.table("testimonies").select("id, summary").not_.is_("summary", None).limit(limit).execute().data
    samples: List[str] = []
    for r in res:
        s = r.get("summary")
        if isinstance(s, str) and s.strip():
            samples.append(s.replace("\n", " "))
    return samples


def embed_texts(client: OpenAI, texts: List[str], model: str) -> np.ndarray:
    emb_batch = 64
    all_vecs: List[np.ndarray] = []
    for i in range(0, len(texts), emb_batch):
        batch = texts[i : i + emb_batch]
        resp = client.embeddings.create(model=model, input=batch)
        vecs = [np.array(d.embedding, dtype=np.float32) for d in resp.data]
        all_vecs.extend(vecs)
    return np.vstack(all_vecs)


def cosine_topk(matrix: np.ndarray, query_vec: np.ndarray, k: int = 3) -> List[Tuple[int, float]]:
    A = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-8)
    q = query_vec / (np.linalg.norm(query_vec) + 1e-8)
    sims = A @ q
    idx = np.argsort(-sims)[:k]
    return [(int(i), float(sims[i])) for i in idx]


def main():
    print("=== Embedding Eval (semantic search) ===")

    # Data source selection
    print("Choose data source:")
    print("1) Local file (one summary per line)")
    print("2) Supabase (up to 350 summaries)")
    src_choice = input("Enter 1/2: ").strip()

    samples: List[str] = []
    if src_choice == "2":
        fetch_limit = int(os.getenv("EMBED_FETCH_LIMIT", "350"))
        try:
            samples = fetch_summaries_from_supabase(fetch_limit)
            print(f"Loaded {len(samples)} samples from Supabase (limit={fetch_limit})")
        except Exception as e:
            print(f"Error loading from Supabase: {e}")
            sys.exit(1)
    else:
        samples_path = Path(os.getenv("EMBED_SAMPLES_FILE", DEFAULT_SAMPLES))
        if not samples_path.exists():
            print(f"Samples file not found: {samples_path}")
            print("Create it with one summary per line.")
            sys.exit(1)
        samples = read_blocks(samples_path)
        if not samples:
            print("No samples found in file.")
            sys.exit(1)
        print(f"Loaded {len(samples)} samples from {samples_path}")

    client = OpenAI()
    print("Choose model option:")
    print("1) text-embedding-3-small (1536)")
    print("2) text-embedding-3-large (3072)")
    print("3) Compare both side-by-side")
    choice = input("Enter 1/2/3: ").strip()

    selected = []
    if choice == "1":
        selected = [MODELS[0]]
    elif choice == "2":
        selected = [MODELS[1]]
    else:
        selected = MODELS

    model_to_emb = {}
    for model, dim in selected:
        print(f"Embedding {len(samples)} samples with {model}...")
        vecs = embed_texts(client, samples, model)
        if vecs.shape[1] != dim:
            print(f"Warning: expected dim {dim}, got {vecs.shape[1]}")
        model_to_emb[model] = vecs
    print("Ready. Type queries; empty line to exit.\n")

    while True:
        q = input("Query: ").strip()
        if not q:
            break
        for model, dim in selected:
            q_vec = embed_texts(client, [q], model)[0]
            topk = cosine_topk(model_to_emb[model], q_vec, k=3)
            print(f"\nModel: {model}")
            for rank, (i, score) in enumerate(topk, 1):
                print(f"- {rank}. score={score:.4f}")
                preview = samples[i]
                print(f"  {preview}")
        print()


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set.")
        sys.exit(1)
    main()
