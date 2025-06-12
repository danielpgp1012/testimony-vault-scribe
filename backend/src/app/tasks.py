import os
import json
import traceback

from celery import Celery
from openai import OpenAI

from .crud import update_testimony
from .deps import get_supabase

# --- Celery Configuration ---
# Create Celery app instance
celery = Celery("testimony_transcriber")

# Configure broker and backend (Redis)
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
celery.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Task routing
    task_routes={
        "transcribe_testimony": {"queue": "transcription"},
    },
    # Worker configuration
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=10,
)

# --- Configuration & Clients (Ensure ENV VARS are set) ---
# Initialize clients only if not running flower
SKIP_CLIENT_INIT = os.environ.get("SKIP_CLIENT_INIT", "false").lower() == "true"

if not SKIP_CLIENT_INIT:
    try:
        openai_client = OpenAI()  # Uses OPENAI_API_KEY environment variable
        print("OpenAI client initialized.")
    except Exception as e:
        print(f"Warning: Failed to initialize OpenAI client: {e}")
        openai_client = None
else:
    print("Skipping client initialization (SKIP_CLIENT_INIT=true)")
    openai_client = None


def update_db_status(testimony_id, status, transcript=None):
    """Update testimony status and transcript in Supabase"""
    try:
        supabase = get_supabase()
        update_data = {"transcript_status": status}
        if transcript:
            update_data["transcript"] = transcript

        update_testimony(supabase, testimony_id, update_data)
        print(
            f"[DB] Updated testimony {testimony_id}: status='{status}', transcript_length={len(transcript) if transcript else 0}"
        )
    except Exception as e:
        print(f"ERROR updating DB for testimony {testimony_id}: {e}")
        traceback.print_exc()


@celery.task(bind=True, max_retries=3, default_retry_delay=60, name="transcribe_testimony")
def transcribe_testimony(self, testimony_id: int, file_path: str):
    """
    Transcribe testimony audio using OpenAI Whisper API.

    Args:
        testimony_id: The ID of the testimony in the database
        file_path: Path to the audio file on the shared volume
    """
    print(f"\n--- [CELERY TASK] Transcribing testimony {testimony_id} from {file_path} ---")
    print(f"Task ID: {self.request.id}")

    # Check if clients are available
    if openai_client is None:
        error_msg = "Required clients not initialized. Cannot process transcription."
        print(f"ERROR: {error_msg}")
        update_db_status(testimony_id, "failed")
        raise RuntimeError(error_msg)

    update_db_status(testimony_id, "processing")

    # Process the audio file directly
    try:
        # Open the audio file and send to Whisper
        with open(file_path, "rb") as audio_file:
            print("Sending to OpenAI Whisper API...")
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",  # Using whisper-1 model for better language support
                file=audio_file,
                language="es",  # Primary language is Spanish
                response_format="text",
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
        # Clean up audio file
        if os.path.exists(file_path):
            try:
                os.unlink(file_path)
                print(f"Cleaned up audio file: {file_path}")
            except Exception as e:
                print(f"Warning: Could not delete audio file {file_path}: {e}")
        print(f"--- Finished testimony {testimony_id} ---")


def tag_testimony(transcription: str):
    """
    Tag testimony transcription using OpenAI API.
    Args:
        transcription: Text transcription of testimony
    """

    def get_metacategories_tags(d):
        return list(d.keys())

    def get_categories_tags(d):
        tags = set()
        for v in d.values():
            if isinstance(v, dict):
                tags.update(v.keys())
        return list(tags)

    def get_all_tag_names(d):
        tags = set()
        for k, v in d.items():
            tags.add(k)
            if isinstance(v, dict):
                tags.update(get_all_tag_names(v))
        return list(tags)

    def get_inner_tag_names(d):
        tags = set()
        for k, v in d.items():
            if isinstance(v, dict):
                tags.update(get_inner_tag_names(v))
            elif v:  # If it's a leaf and True
                tags.add(k)
        return list(tags)

    system_prompt = """You are a multilabel classifier.
Given a piece of text and the taxonomy below, assign all relevant labels from the taxonomy.
Return the labels as a nested JSON dictionary, where each label is marked `true` at the deepest relevant level.
Use only the labels provided in the taxonomy. Do not invent or combine labels. If no label applies, return an empty dictionary.
Preserve the full taxonomy path and hierarchy in the output.

Material
-> Salud
---> Enfermedad
---> Accidente
---> Bienestar Mental
-> Economía
---> Casa
---> Carro
---> Deudas
---> Ingresos
---> Ahorros
---> Gastos
-> Familia
---> Pareja
---> Hijos
---> Padres
---> Hermanos
---> Familia Cercana
-> Amistades
---> Amigos Cercanos
---> Conocidos
---> Sociedad
-> Profesional
---> Estudios
---> Trabajo
---> Emprendimiento
---> Jubilación

Espiritual
-> Desarrollo Personal
---> Identificar Tendencias
---> Vencer Tendencias
-> Vida Espiritual
---> Oración
---> Obediencia
---> Frutos
---> Leer biblia
---> Leer libro vivencias
---> Cantar a capela
---> Valor Hermana Maria Luisa
---> Congregación
---> Diezmo
---> Labores Espirituales

An user input example:
Estoy agradecido por el apoyo de mis padres, hermanos y amigos cercanos durante mi enfermedad y por poder ahorrar algo de dinero este mes.

An expected assistant output:
{
  "Material": {
    "Salud": {
      "Enfermedad": true
    },
    "Economía": {
      "Ahorros": true
    },
    "Familia": {
      "Padres": true,
      "Hermanos": true
    },
    "Amistades": {
      "Amigos Cercanos": true
    }
  }
}
"""

    response = openai_client.responses.create(
        model="gpt-4.1",
        instructions=system_prompt,
        input=transcription,
    )

    tags_structured = json.loads(response.output_text)
    metacategories = get_metacategories_tags(tags_structured)
    categories = get_categories_tags(tags_structured)
    tags_all = get_all_tag_names(tags_structured)
    tags = get_inner_tag_names(tags_structured)
    return tags, categories, metacategories, tags_structured, tags_all


# --- Local Test ---
if __name__ == "__main__":
    TEST_FILE = "sample_audio_files/2024.11.24.Testimonio 2.mp3"
    TEST_ID = 1

    if not os.path.exists(TEST_FILE):
        print(f"ERROR: Test file not found: {TEST_FILE}")
    elif openai_client is not None:
        transcribe_testimony.delay(TEST_ID, TEST_FILE)
    else:
        print("OpenAI client not initialized")
