from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import uuid, os

from .schemas import TestimonyOut
from .deps import get_supabase, get_gcs_client
from .crud import insert_testimony, check_duplicate_testimony, get_testimony_by_id
from .tasks import transcribe_testimony
from .utils import get_audio_metadata
import logging
LOGGER = logging.getLogger(__name__)

GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]
app = FastAPI(title="Church Testimony Backend")

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/testimonies", response_model=TestimonyOut, status_code=201)
async def create_testimony(
    # title: str = Form(...),
    church_id: Optional[str] = Form(None),
    # date: str = Form(...),
    tags: Optional[str] = Form(None),
    file: UploadFile = File(...),
    supabase=Depends(get_supabase),
    gcs_client=Depends(get_gcs_client),
):
    # Read file content
    file_bytes = await file.read()
    
    # Extract metadata and generate audio fingerprint
    sample_rate, channels, duration_ms, audio_hash = get_audio_metadata(file_bytes, file.filename)
    
    if not audio_hash:
        raise HTTPException(status_code=400, detail="Could not process audio file")
    
    # Check for duplicates before uploading to GCS
    duplicate_id = check_duplicate_testimony(supabase, 
                                           church_id=church_id,
                                           audio_hash=audio_hash)
    
    if duplicate_id:
        # If duplicate found, return existing testimony
        existing_testimony = get_testimony_by_id(supabase, duplicate_id)
        if existing_testimony and existing_testimony["transcript_status"] == "completed":
            return JSONResponse(
                content={"id": duplicate_id, **existing_testimony, "duplicate": True},
                status_code=200
            )
    
    # Upload to GCS if no duplicate was found
    file_extension = os.path.splitext(file.filename)[1]
    gcs_filename = f"testimony_audio/{uuid.uuid4()}{file_extension}"
    
    bucket = gcs_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(gcs_filename)
    blob.upload_from_string(file_bytes, content_type=file.content_type)
    
    # Create GCS URI
    storage_url = f"gs://{GCS_BUCKET_NAME}/{gcs_filename}"
    
    # 2. Insert pending row in Supabase with audio metadata
    now = datetime.utcnow().isoformat()
    testimony_data = {
        # "title": title,
        # "date": date,
        "tags": [t.strip() for t in tags.split(",")] if tags else [],
        "storage_url": storage_url,
        "transcript_status": "pending",
        "created_at": now,
        "updated_at": now,
        "audio_hash": audio_hash,
        "audio_duration_ms": duration_ms,
        "sample_rate": sample_rate,
        "channels": channels,
        "user_file_name": file.filename
    }
    
    # Only add church_id if it was provided
    if church_id:
        testimony_data["church_id"] = church_id
        
    testimony_id = insert_testimony(supabase, testimony_data)

    # 3. Kick off async transcription with metadata
    transcribe_testimony(
        testimony_id, 
        storage_url,
        sample_rate=sample_rate,
        channels=channels,
        duration_ms=duration_ms
    )

    row = (
        supabase.table("testimonies")
        .select("*")
        .eq("id", testimony_id)
        .single()
        .execute()
        .data
    )
    return JSONResponse(content=row, status_code=201)

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
