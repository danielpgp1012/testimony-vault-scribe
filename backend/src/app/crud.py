from typing import Any, Dict, Optional

from supabase import Client


def insert_testimony(sb: Client, data: Dict[str, Any]) -> int:
    res = sb.table("testimonies").insert(data).execute()
    return res.data[0]["id"]


def update_testimony(sb: Client, tid: int, fields: Dict[str, Any]) -> None:
    sb.table("testimonies").update(fields).eq("id", tid).execute()


def check_duplicate_testimony(
    sb: Client,
    audio_hash: Optional[str],
    church_id: Optional[str] = None,
) -> Optional[int]:
    """
    Check if a testimony with the same storage_url or audio_hash already exists.
    Also checks church_id if provided.
    Returns the testimony ID if found, None otherwise.
    """

    query = sb.table("testimonies").select("id").eq("audio_hash", audio_hash)
    if church_id is not None:
        query = query.eq("church_id", church_id)

    result = query.execute()

    if result.data and len(result.data) > 0:
        return result.data[0]["id"]

    return None


def get_testimony_by_id(sb: Client, testimony_id: int) -> Optional[Dict[str, Any]]:
    """Get a testimony by ID"""
    result = sb.table("testimonies").select("*").eq("id", testimony_id).single().execute()
    return result.data if result.data else None


def insert_testimony_chunks(sb: Client, rows: list[Dict[str, Any]]) -> None:
    """Bulk insert transcript chunks for semantic search."""
    if not rows:
        return
    sb.table("testimony_chunks").insert(rows).execute()


def update_testimony_with_indexing(sb: Client, tid: int, fields: Dict[str, Any]) -> None:
    """Update testimony and index transcript chunks if provided."""
    update_testimony(sb, tid, fields)

    transcript = fields.get("transcript")
    if transcript:
        from semantic.index_testimonies import index_transcript

        index_transcript(sb, tid, transcript)
