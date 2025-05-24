import os
import uuid
import traceback
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
from google.protobuf.json_format import MessageToDict
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
import tempfile

from .deps import get_supabase
from .crud import update_testimony

# --- Configuration & Clients (Ensure ENV VARS are set) ---
GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]
try:
    speech_client = speech.SpeechClient()
    storage_client = storage.Client()
    print("Clients initialized.")
except Exception as e:
    raise RuntimeError(f"Failed to initialize Google Cloud clients: {e}")

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

def get_audio_metadata(local_path):
    """Gets sample rate, channels, duration_ms. Returns (None, None, None) on error."""
    try:
        if not os.path.exists(local_path): raise FileNotFoundError(f"File not found: {local_path}")
        audio = AudioSegment.from_file(local_path)
        print(f"Metadata: Rate={audio.frame_rate}Hz, Channels={audio.channels}, Duration={len(audio)/1000:.2f}s")
        if audio.frame_rate <= 0 or audio.channels <= 0 or len(audio) == 0:
            raise ValueError("Invalid metadata extracted (<= 0)")
        return audio.frame_rate, audio.channels, len(audio)
    except Exception as e:
        print(f"ERROR getting metadata for {local_path}: {e}")
        return None, None, None

def transcribe_testimony(testimony_id: int, gcs_uri: str, sample_rate: int = None, channels: int = None, duration_ms: int = None):
    """
    Transcribe testimony audio using Google Speech-to-Text API.
    
    Args:
        testimony_id: The ID of the testimony in the database
        gcs_uri: The GCS URI of the audio file
        sample_rate: Optional sample rate in Hz
        channels: Optional number of audio channels
        duration_ms: Optional duration in milliseconds
    """
    print(f"\n--- Transcribing testimony {testimony_id} from {gcs_uri} ---")
    update_db_status(testimony_id, "processing")
    
    # Extract the blob name from the GCS URI (for logging only)
    blob_name = gcs_uri.replace(f"gs://{GCS_BUCKET_NAME}/", "")
    
    try:
        # If metadata is not provided, we'll use defaults or guess
        if not all([sample_rate, channels, duration_ms]):
            print("Warning: Missing audio metadata, using defaults")
            sample_rate = sample_rate or 44100  # Default to CD quality
            channels = channels or 1  # Default to mono
            duration_ms = duration_ms or 600000  # Default to 10 minutes
        else:
            print(f"Using provided metadata: Rate={sample_rate}Hz, Channels={channels}, Duration={duration_ms/1000:.2f}s")
        
        # Configure API Request
        config = speech.RecognitionConfig(
            # encoding determined by extension or default to MP3 if needed
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            sample_rate_hertz=sample_rate,
            language_code="es-ES",
            audio_channel_count=channels,
            enable_automatic_punctuation=True,
            alternative_language_codes=["fr-FR", "pt-PT"],
            model="latest_long" # Optional: Try different models
        )
        audio = speech.RecognitionAudio(uri=gcs_uri)
        print(f"Sending API request with config: {config}")

        # Start and wait for Job
        operation = speech_client.long_running_recognize(config=config, audio=audio)
        print(f"Operation started: {operation.operation.name}. Waiting...")
        # Adjust timeout: duration in seconds * ~0.6 + buffer (e.g., 600s)
        timeout = (duration_ms / 1000 * 0.6) + 600
        response = operation.result(timeout=timeout)
        print("Operation finished.")

        # *** Log RAW response for debugging ***
        print("--- RAW API RESPONSE ---")
        print(MessageToDict(response._pb))
        print("--- END RAW RESPONSE ---")

        # Process Results
        transcript = " ".join(
            alt.transcript for res in response.results for alt in res.alternatives
        ).strip()

        if transcript:
            print("Transcription successful.")
            update_db_status(testimony_id, "completed", transcript)
        else:
            print("WARNING: Transcription result is empty.")
            update_db_status(testimony_id, "completed_empty")

    except Exception as e:
        print(f"--- ERROR processing testimony {testimony_id} ---")
        traceback.print_exc()
        update_db_status(testimony_id, "failed")
    finally:
        print(f"--- Finished testimony {testimony_id} ---")


# --- Local Test ---
if __name__ == "__main__":
    # REQUIRES: ENV VARS (GOOGLE_APPLICATION_CREDENTIALS, GCS_BUCKET_NAME), ffmpeg, libraries
    TEST_FILE = "sample_audio_files/2024.11.24.Testimonio 2.mp3" # Change path if needed
    TEST_ID = 1

    if not os.path.exists(TEST_FILE):
        print(f"ERROR: Test file not found: {TEST_FILE}")
    else:
        # For testing, upload to GCS first and extract metadata
        try:
            # Get metadata
            audio = AudioSegment.from_file(TEST_FILE)
            sample_rate = audio.frame_rate
            channels = audio.channels
            duration_ms = len(audio)
            
            # Upload to GCS
            blob_name = f"testimony_audio/test_{TEST_ID}.mp3"
            bucket = storage_client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(TEST_FILE)
            gcs_uri = f"gs://{GCS_BUCKET_NAME}/{blob_name}"
            
            # Transcribe with metadata
            transcribe_testimony(
                TEST_ID, 
                gcs_uri, 
                sample_rate=sample_rate,
                channels=channels,
                duration_ms=duration_ms
            )
        finally:
            try:
                # Clean up the test file
                storage_client.bucket(GCS_BUCKET_NAME).blob(blob_name).delete()
            except:
                print("Warning: Cleanup failed")