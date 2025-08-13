import hashlib
from typing import Any, Dict, List, Optional

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


def get_testimony_by_id(sb: Client, testimony_id: str) -> Optional[Dict[str, Any]]:
    """Get a testimony by ID"""
    result = sb.table("testimonies").select("*").eq("id", testimony_id).single().execute()
    return result.data if result.data else None


def get_or_create_summary_prompt(
    sb: Client,
    *,
    name: str,
    version: str,
    prompt_template: str,
    model_name: str,
    temperature: float,
    max_tokens: int,
) -> int:
    """Return the id of the summary_prompts row matching the prompt+model+version, creating it if needed."""
    template_hash = hashlib.sha256(f"{prompt_template}|{model_name}|{version}".encode()).hexdigest()

    # Try find by unique template_hash
    query = sb.table("summary_prompts").select("id").eq("template_hash", template_hash).limit(1).execute()
    if query and getattr(query, "data", None):
        rows = query.data
        if isinstance(rows, list) and len(rows) > 0:
            return rows[0]["id"]

    res = (
        sb.table("summary_prompts")
        .insert(
            {
                "name": name,
                "version": version,
                "prompt_template": prompt_template,
                "model_name": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "template_hash": template_hash,
                "is_active": True,
            }
        )
        .execute()
    )
    return res.data[0]["id"]


def update_testimony_summary_with_prompt(sb: Client, tid: int, summary: str, summary_prompt_id: int) -> None:
    sb.table("testimonies").update({"summary": summary, "summary_prompt_id": summary_prompt_id}).eq("id", tid).execute()


def upsert_testimony_embedding(sb: Client, tid: int, embedding: List[float]) -> None:
    """Upsert a single embedding per testimony (no history)."""
    sb.table("testimony_embeddings").upsert(
        {"testimony_id": tid, "embedding": embedding},
        on_conflict="testimony_id",
    ).execute()
