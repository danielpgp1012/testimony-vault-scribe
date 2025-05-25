from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import Page, add_pagination, paginate
from fastapi_pagination.utils import disable_installed_extensions_check
from typing import List, Optional
from datetime import datetime
import uuid, os

from .schemas import TestimonyOut, ChurchLocation
from .deps import get_supabase, get_gcs_client
from .crud import insert_testimony, check_duplicate_testimony, get_testimony_by_id
from .tasks import transcribe_testimony, celery
from .utils import get_audio_metadata
import logging
LOGGER = logging.getLogger(__name__)

GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB in bytes

app = FastAPI(title="Church Testimony Backend")

# Disable fastapi-pagination extensions check to avoid warnings
disable_installed_extensions_check()

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add pagination to the app
add_pagination(app)

@app.post("/testimonies", response_model=TestimonyOut, status_code=201)
async def create_testimony(
    # title: str = Form(...),
    church_id: Optional[str] = Form(ChurchLocation.LAUSANNE.value),
    # date: str = Form(...),
    tags: Optional[str] = Form(None),
    file: UploadFile = File(...),
    # recorded_at should be timestamp compatible with supabase timestampz
    recorded_at: Optional[str] = Form(None),
    supabase=Depends(get_supabase),
    gcs_client=Depends(get_gcs_client),
):
    # Check file size limit
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE / (1024 * 1024):.0f} MB")
    
    # Validate church_id against enum values
    if church_id and church_id not in [location.value for location in ChurchLocation]:
        raise HTTPException(status_code=400, detail=f"Invalid church_id. Must be one of: {[location.value for location in ChurchLocation]}")
    
    # Use Lausanne as default if no church_id provided
    if not church_id:
        church_id = ChurchLocation.LAUSANNE.value
    
    # Extract metadata and generate audio fingerprint
    duration_ms, audio_hash = get_audio_metadata(file_bytes, file.filename)
    
    if not audio_hash:
        raise HTTPException(status_code=400, detail="Could not process audio file")
    
    # Handle recorded_at - use current date as fallback if not provided
    now = datetime.utcnow()
    recorded_at_date = None
    if recorded_at:
        try:
            # Parse the date string (YYYY-MM-DD format)
            from datetime import date
            recorded_date = date.fromisoformat(recorded_at)
            recorded_at_date = recorded_date.isoformat()  # This will be YYYY-MM-DD format
        except ValueError:
            # If parsing fails, use current date
            recorded_at_date = now.date().isoformat()
    else:
        # If not provided, use current date
        recorded_at_date = now.date().isoformat()
    
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
    gcs_filename = f"testimony_audio/{file.filename}"
    
    bucket = gcs_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(gcs_filename)
    blob.upload_from_string(file_bytes, content_type=file.content_type)
    
    # Create GCS URI
    storage_url = f"gs://{GCS_BUCKET_NAME}/{gcs_filename}"
    
    # 2. Insert pending row in Supabase with audio metadata
    now_iso = now.isoformat()
    testimony_data = {
        # "title": title,
        # "date": date,
        "tags": [t.strip() for t in tags.split(",")] if tags else [],
        "storage_url": storage_url,
        "transcript_status": "pending",
        "created_at": now_iso,
        "updated_at": now_iso,
        "recorded_at": recorded_at_date,
        "audio_hash": audio_hash,
        "audio_duration_ms": duration_ms,
        "user_file_name": file.filename,
        "church_id": church_id  # Always include church_id now
    }
        
    testimony_id = insert_testimony(supabase, testimony_data)

    # 3. Kick off async transcription
    task = celery.send_task('transcribe_testimony', args=[testimony_id, storage_url])

    row = (
        supabase.table("testimonies")
        .select("*")
        .eq("id", testimony_id)
        .single()
        .execute()
        .data
    )
    
    # Add task ID to response
    row["task_id"] = task.id
    
    return JSONResponse(content=row, status_code=201)

@app.get("/testimonies", response_model=Page[TestimonyOut])
def list_testimonies(
    church_id: Optional[str] = None,
    transcript_status: Optional[str] = None,
    supabase=Depends(get_supabase)
):
    query = supabase.table("testimonies").select("*")
    
    # Apply filters if provided
    if church_id:
        query = query.eq("church_id", church_id)
    
    if transcript_status:
        query = query.eq("transcript_status", transcript_status)
    
    data = query.order("recorded_at", desc=True).execute().data
    return paginate(data)

@app.get("/testimonies/{testimony_id}", response_model=TestimonyOut)
def get_testimony(testimony_id: int, supabase=Depends(get_supabase)):
    """Get a specific testimony by ID"""
    testimony = get_testimony_by_id(supabase, testimony_id)
    if not testimony:
        raise HTTPException(status_code=404, detail="Testimony not found")
    return testimony

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    """Get the status of a Celery task"""
    task_result = celery.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None,
        "traceback": task_result.traceback if task_result.failed() else None,
    }

@app.get("/worker/stats")
def get_worker_stats():
    """Get Celery worker statistics"""
    try:
        inspect = celery.control.inspect()
        stats = inspect.stats()
        active = inspect.active()
        reserved = inspect.reserved()
        
        return {
            "stats": stats,
            "active_tasks": active,
            "reserved_tasks": reserved,
        }
    except Exception as e:
        return {"error": f"Could not get worker stats: {str(e)}"}
