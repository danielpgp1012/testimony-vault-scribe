import os
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


def update_db_status(testimony_id, status, transcript=None, summary=None):
    """Update testimony status, transcript, and summary in Supabase"""
    try:
        supabase = get_supabase()
        update_data = {"transcript_status": status}
        if transcript:
            update_data["transcript"] = transcript
        if summary:
            update_data["summary"] = summary

        update_testimony(supabase, testimony_id, update_data)
        print(
            f"[DB] Updated testimony {testimony_id}: status='{status}', transcript_length={len(transcript) if transcript else 0}, summary_length={len(summary) if summary else 0}"
        )
    except Exception as e:
        print(f"ERROR updating DB for testimony {testimony_id}: {e}")
        traceback.print_exc()


def generate_summary(transcript: str) -> str:
    """Generate a concise summary of the testimony transcript."""
    if not transcript or openai_client is None:
        return ""

    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres un asistente lingüístico experto de la iglesia de Dios Ministerial de Jesucristo "
                    "Internacional, que es una iglesia neo-pentecostal con énfasis en la obra del Espíritu Santo y "
                    "el don de profecía, donde Dios habla a las personas y les hace promesas que las consuelan, "
                    "exhortan y edifican.\n"
                    "Debes elaborar un **resumen claro y conciso** de un testimonio hablado.\n\n"
                    "◼︎ **Extensión**: 100-150 palabras.\n"
                    "◼︎ **Estilo**: narración fluida, tercera persona identificando si es hombre o mujer, sin muletillas ni repeticiones.\n"
                    "◼︎ **Incluye**\n"
                    "   1. **Promesa o profecía recibida** (qué dijo el Señor y en qué contexto de la vida de la persona "
                    "(si disponible)?).\n"
                    "   2. **Proceso y manifestación**: Cómo se cumplió la promesa y desenlace resultado (milagro, "
                    "cambio personal, puerta abierta, etc.).\n"
                    "   3. **Lección edificante para la iglesia**: enseñanza principal que el hermano(a) quiere transmitir.\n\n"
                    "Si el testimonio cita un pasaje bíblico, inclúyelo dentro del resumen. No añadas texto fuera del resumen principal.\n"
                    "No añadas texto fuera de este formato."
                ),
            },
            {
                "role": "user",
                "content": f"Transcripción del testimonio:\n{transcript}",
            },
        ]

        response = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            max_tokens=250,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"ERROR generating summary: {e}")
        traceback.print_exc()
        return ""


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
            summary = generate_summary(transcript)
            if summary:
                print(f"Summary generated: {summary[:200]}...")
            update_db_status(testimony_id, "completed", transcript, summary)
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
