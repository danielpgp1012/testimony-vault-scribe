from app.crud import insert_testimony_chunks
from app.deps import get_supabase
from tqdm import tqdm

from .chunker import make_chunks
from .embedder import embed_texts


def index_transcript(sb, testimony_id: int, transcript: str) -> None:
    """Chunk and embed a transcript, storing vectors via Supabase."""
    chunks = list(make_chunks(transcript))
    vectors = embed_texts([c["text"] for c in chunks])
    rows = [
        {
            "testimony_id": testimony_id,
            "chunk_index": c["idx"],
            "text": c["text"],
            "tokens": c["tokens"],
            "embedding": vec,
        }
        for c, vec in zip(chunks, vectors)
    ]
    insert_testimony_chunks(sb, rows)


def main():
    sb = get_supabase()

    testimonies = sb.table("testimonies").select("id", "transcript").execute().data
    indexed = sb.table("testimony_chunks").select("testimony_id").execute().data
    indexed_ids = {r["testimony_id"] for r in indexed}

    for row in tqdm(testimonies, desc="Indexing"):
        if row["id"] not in indexed_ids and row.get("transcript"):
            index_transcript(sb, row["id"], row["transcript"])

    print("✅ Indexing complete")


if __name__ == "__main__":
    main()
