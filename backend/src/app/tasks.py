import os
import uuid
import traceback
import tempfile
from openai import OpenAI
from google.cloud import storage
from celery import Celery

from .deps import get_supabase
from .crud import update_testimony

# --- Celery Configuration ---
# Create Celery app instance
celery = Celery('testimony_transcriber')

# Configure broker and backend (Redis)
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
celery.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # Task routing
    task_routes={
        'transcribe_testimony': {'queue': 'transcription'},
    },
    # Worker configuration
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=10,
)

# --- Configuration & Clients (Ensure ENV VARS are set) ---
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")

# Initialize clients only if not running flower
SKIP_CLIENT_INIT = os.environ.get("SKIP_CLIENT_INIT", "false").lower() == "true"

if not SKIP_CLIENT_INIT:
    try:
        storage_client = storage.Client()
        openai_client = OpenAI()  # Uses OPENAI_API_KEY environment variable
        print("Clients initialized.")
    except Exception as e:
        print(f"Warning: Failed to initialize clients: {e}")
        storage_client = None
        openai_client = None
else:
    print("Skipping client initialization (SKIP_CLIENT_INIT=true)")
    storage_client = None
    openai_client = None

def update_db_status(testimony_id, status, transcript=None):
    """Update testimony status and transcript in Supabase"""
    try:
        supabase = get_supabase()
        update_data = {"transcript_status": status}
        if transcript:
            update_data["transcript"] = transcript
        
        update_testimony(supabase, testimony_id, update_data)
        print(f"[DB] Updated testimony {testimony_id}: status='{status}', transcript_length={len(transcript) if transcript else 0}")
    except Exception as e:
        print(f"ERROR updating DB for testimony {testimony_id}: {e}")
        traceback.print_exc()

def download_from_gcs(gcs_uri, local_path):
    """Download file from GCS to local path"""
    try:
        # Extract bucket name and blob name from GCS URI
        if not gcs_uri.startswith("gs://"):
            raise ValueError(f"Invalid GCS URI: {gcs_uri}")
        
        # Remove gs:// prefix and split into bucket and blob
        path_parts = gcs_uri[5:].split("/", 1)
        if len(path_parts) != 2:
            raise ValueError(f"Invalid GCS URI format: {gcs_uri}")
        
        bucket_name, blob_name = path_parts
        
        # Download the file
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(local_path)
        print(f"Downloaded {gcs_uri} to {local_path}")
        
    except Exception as e:
        print(f"ERROR downloading from GCS: {e}")
        raise

@celery.task(bind=True, max_retries=3, default_retry_delay=60, name='transcribe_testimony')
def transcribe_testimony(self, testimony_id: int, gcs_uri: str):
    """
    Transcribe testimony audio using OpenAI Whisper API.
    
    Args:
        testimony_id: The ID of the testimony in the database
        gcs_uri: The GCS URI of the audio file
    """
    print(f"\n--- [CELERY TASK] Transcribing testimony {testimony_id} from {gcs_uri} ---")
    print(f"Task ID: {self.request.id}")
    
    # Check if clients are available
    if storage_client is None or openai_client is None:
        error_msg = "Required clients not initialized. Cannot process transcription."
        print(f"ERROR: {error_msg}")
        update_db_status(testimony_id, "failed")
        raise RuntimeError(error_msg)
    
    update_db_status(testimony_id, "processing")
    
    # Create a temporary file for the audio
    temp_file = None
    try:
        # Create temporary file with appropriate extension
        file_extension = os.path.splitext(gcs_uri)[1] or '.mp3'
        temp_file = tempfile.NamedTemporaryFile(suffix=file_extension, delete=False)
        temp_file.close()
        
        # Download audio file from GCS
        print(f"Downloading audio file from {gcs_uri}")
        download_from_gcs(gcs_uri, temp_file.name)
        
        # Open the audio file and send to Whisper
        with open(temp_file.name, "rb") as audio_file:
            print("Sending to OpenAI Whisper API...")
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",  # Using whisper-1 model for better language support
                file=audio_file,
                language="es",  # Primary language is Spanish
                response_format="text"
            )
        
        transcript = transcription.strip() if transcription else ""
        
        if transcript:
            print("Transcription successful.")
            print(f"Transcript preview: {transcript[:200]}...")
            update_db_status(testimony_id, "completed", transcript)
        else:
            print("WARNING: Transcription result is empty.")
            update_db_status(testimony_id, "completed_empty")

    except Exception as e:
        print(f"--- ERROR processing testimony {testimony_id} ---")
        print(f"Error: {str(e)}")
        traceback.print_exc()
        
        # Retry logic for certain types of errors
        if "rate limit" in str(e).lower() or "timeout" in str(e).lower():
            print(f"Retrying task due to {str(e)}...")
            try:
                self.retry(countdown=60 * (self.request.retries + 1))
            except self.MaxRetriesExceededError:
                print("Max retries exceeded, marking as failed")
                update_db_status(testimony_id, "failed")
        else:
            update_db_status(testimony_id, "failed")
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
                print(f"Cleaned up temporary file: {temp_file.name}")
            except Exception as e:
                print(f"Warning: Could not delete temporary file {temp_file.name}: {e}")
        print(f"--- Finished testimony {testimony_id} ---")


# --- Local Test ---
if __name__ == "__main__":
    # REQUIRES: ENV VARS (GOOGLE_APPLICATION_CREDENTIALS, GCS_BUCKET_NAME, OPENAI_API_KEY)
    TEST_FILE = "sample_audio_files/2024.11.24.Testimonio 2.mp3" # Change path if needed
    TEST_ID = 1

    if not os.path.exists(TEST_FILE):
        print(f"ERROR: Test file not found: {TEST_FILE}")
    else:
        # For testing, upload to GCS first
        try:
            # Upload to GCS
            blob_name = f"testimony_audio/test_{TEST_ID}.mp3"
            bucket = storage_client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(TEST_FILE)
            gcs_uri = f"gs://{GCS_BUCKET_NAME}/{blob_name}"
            
            # Transcribe
            transcribe_testimony.delay(TEST_ID, gcs_uri)
        finally:
            try:
                # Clean up the test file
                storage_client.bucket(GCS_BUCKET_NAME).blob(blob_name).delete()
            except:
                print("Warning: Cleanup failed")