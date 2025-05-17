from typing import Dict, Any, List, Optional
from supabase import Client

def insert_testimony(sb: Client, data: Dict[str, Any]) -> int:
    res = sb.table("testimonies").insert(data).execute()
    return res.data[0]["id"]

def update_testimony(sb: Client, tid: int, fields: Dict[str, Any]) -> None:
    sb.table("testimonies").update(fields).eq("id", tid).execute()

def check_duplicate_testimony(sb: Client,audio_hash: Optional[str], church_id: Optional[str] = None, ) -> Optional[int]:
    """
    Check if a testimony with the same storage_url or audio_hash already exists.
    Also checks church_id if provided.
    Returns the testimony ID if found, None otherwise.
    """
        
    query = sb.table("testimonies").select("id").eq("audio_hash", audio_hash)
    if church_id:
        query = query.eq("church_id", church_id)
    result = query.execute()
    
    if result.data and len(result.data) > 0:
        return result.data[0]["id"]
            
    return None

def get_testimony_by_id(sb: Client, testimony_id: int) -> Optional[Dict[str, Any]]:
    """Get a testimony by ID"""
    result = sb.table("testimonies").select("*").eq("id", testimony_id).single().execute()
    return result.data if result.data else None
