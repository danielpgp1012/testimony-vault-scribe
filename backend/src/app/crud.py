
from typing import Dict, Any
from supabase import Client

def insert_testimony(sb: Client, data: Dict[str, Any]) -> int:
    res = sb.table("testimonies").insert(data).execute()
    return res.data[0]["id"]

def update_testimony(sb: Client, tid: int, fields: Dict[str, Any]) -> None:
    sb.table("testimonies").update(fields).eq("id", tid).execute()
