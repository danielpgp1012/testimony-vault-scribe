
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
import uuid, os

from googleapiclient.http import MediaInMemoryUpload

from .schemas import TestimonyOut
from .deps import get_supabase, get_drive
from .crud import insert_testimony
from .tasks import transcribe_testimony

BUCKET = os.getenv("SUPABASE_BUCKET", "testimonies")
DRIVE_FOLDER = os.getenv("GDRIVE_FOLDER_ID")

app = FastAPI(title="Church Testimony Backend")

@app.post("/testimonies", response_model=TestimonyOut, status_code=201)
async def create_testimony(
    title: str = Form(...),
    speaker: Optional[str] = Form(None),
    date: str = Form(...),
    tags: Optional[str] = Form(None),
    file: UploadFile = File(...),
    supabase=Depends(get_supabase),
    drive=Depends(get_drive),
):
    # 1. Upload to Supabase Storage
    file_bytes = await file.read()
    path = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
    supabase.storage.from_(BUCKET).upload(path, file_bytes)
    storage_url = supabase.storage.from_(BUCKET).get_public_url(path)

    # 2. Backup to Google Drive
    media = MediaInMemoryUpload(file_bytes, mimetype=file.content_type)
    drive_file = (
        drive.files()
        .create(
            body={"name": file.filename, "parents": [DRIVE_FOLDER]},
            media_body=media,
            fields="id",
        )
        .execute()
    )
    drive_id = drive_file["id"]

    # 3. Insert pending row
    now = datetime.utcnow().isoformat()
    testimony_id = insert_testimony(
        supabase,
        {
            "title": title,
            "speaker": speaker,
            "date": date,
            "tags": [t.strip() for t in tags.split(",")] if tags else [],
            "drive_id": drive_id,
            "storage_url": storage_url,
            "transcript_status": "pending",
            "created_at": now,
            "updated_at": now,
        },
    )

    # 4. Kick off async transcription
    transcribe_testimony.delay(testimony_id, storage_url)

    row = (
        supabase.table("testimonies")
        .select("*")
        .eq("id", testimony_id)
        .single()
        .execute()
        .data
    )
    return JSONResponse(row)

@app.get("/testimonies", response_model=List[TestimonyOut])
def list_testimonies(supabase=Depends(get_supabase)):
    data = (
        supabase.table("testimonies")
        .select("*")
        .order("created_at", desc=True)
        .execute()
        .data
    )
    return data
