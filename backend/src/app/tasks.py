import os
import traceback

from celery import Celery
from openai import OpenAI

from .crud import get_or_create_summary_prompt, update_testimony, upsert_testimony_embedding
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


def update_db_status(testimony_id, status, transcript=None, summary=None, summary_prompt_id=None):
    """Update testimony status, transcript, and summary in Supabase"""
    try:
        supabase = get_supabase()
        update_data = {"transcript_status": status}
        if transcript:
            update_data["transcript"] = transcript
        if summary:
            update_data["summary"] = summary
        if summary_prompt_id is not None:
            update_data["summary_prompt_id"] = summary_prompt_id

        update_testimony(supabase, testimony_id, update_data)
        print(
            f"[DB] Updated testimony {testimony_id}: status='{status}', transcript_length={len(transcript) if transcript else 0}, summary_length={len(summary) if summary else 0}"
        )
    except Exception as e:
        print(f"ERROR updating DB for testimony {testimony_id}: {e}")
        traceback.print_exc()


# --- Summary Prompt Configuration ---
SUMMARY_MODEL = os.environ.get("SUMMARY_MODEL", "gpt-4.1-mini")
SUMMARY_TEMPERATURE = float(os.environ.get("SUMMARY_TEMPERATURE", "0.3"))
SUMMARY_MAX_TOKENS = int(os.environ.get("SUMMARY_MAX_TOKENS", "250"))

# Fixed semantic version for the prompt configuration (date belongs in created_at)
SUMMARY_PROMPT_VERSION = os.environ.get("SUMMARY_PROMPT_VERSION", "v2")

CURRENT_SUMMARY_PROMPT = (
    "Eres un asistente lingüístico experto de la iglesia de Dios Ministerial de Jesucristo "
    "Internacional, que es una iglesia neo-pentecostal con énfasis en la obra del Espíritu Santo y "
    "el don de profecía, donde Dios habla a las personas y les hace promesas que las consuelan, "
    "exhortan y edifican.\n"
    "Debes elaborar un **resumen claro y conciso** de un testimonio hablado. Sigue el siguiente "
    "formato en lo posible\n\n"
    "◼︎ **Extensión**: 100-150 palabras.\n"
    "◼︎ **Estilo**: narración fluida, tercera persona, identificando el genero solo cuando sea evidente, sin muletillas ni repeticiones.\n"
    "◼︎ **Incluye**\n"
    "   1. **Promesa o profecía recibida** (qué dijo el Señor y en qué contexto de la vida de la persona "
    "(si disponible)?).\n"
    "   2. **Proceso y manifestación**: Cómo se cumplió la promesa y desenlace resultado (milagro, "
    "cambio personal, puerta abierta, etc.).\n"
    "   3. **Lección edificante para la iglesia**: enseñanza principal que el hermano(a) quiere transmitir.\n\n"
    "Al final, añade 3-7 etiquetas doctrinales (en minúsculas, sin espacios ni acentos) que capturen el "
    "contenido del testimonio para búsqueda semántica y etiquetado doctrinal.\n"
    "Las etiquetas deben:\n"
    "- Estar en minúsculas, sin acentos ni espacios (usa guion_bajo)\n"
    "- Describir tanto la prueba como la virtud manifestada\n"
    "- Ser específicas y características de este testimonio\n"
    "- Evitar términos genéricos como #profecia o #promesa\n\n"
    "Ejemplos: #sanidad #perseverancia #estudios #adicciones #cancer #alabanza #familia #fe\n\n"
    "Formato estricto:\n\n"
    "«Aquí va tu resumen de 100-150 palabras…»\n\n"
    "«Aquí van las etiquetas doctrinales…»\n\n"
    "No añadas texto fuera de este formato."
)


def generate_summary(transcript: str) -> str:
    """Generate a concise summary of the testimony transcript."""
    if not transcript or openai_client is None:
        return ""

    try:
        messages = [
            {
                "role": "system",
                "content": CURRENT_SUMMARY_PROMPT,
            },
            {
                "role": "user",
                "content": f"Transcripción del testimonio:\n{transcript}",
            },
        ]

        response = openai_client.chat.completions.create(
            model=SUMMARY_MODEL,
            messages=messages,
            max_tokens=SUMMARY_MAX_TOKENS,
            temperature=SUMMARY_TEMPERATURE,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"ERROR generating summary: {e}")
        traceback.print_exc()
        return ""


# --- Embeddings Configuration ---
# Global default model; not stored per-row
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")


def generate_embedding_from_summary_text(text: str) -> list:
    """Generate a single embedding for the full summary string (summary + hashtags as one line)."""
    if not text or openai_client is None:
        return []
    try:
        one_line = text.replace("\n", " ")
        resp = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=[one_line])
        return resp.data[0].embedding
    except Exception as e:
        print(f"ERROR generating embedding: {e}")
        traceback.print_exc()
        return []


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
            # Track summary prompt used for this generation
            try:
                supabase = get_supabase()
                prompt_id = get_or_create_summary_prompt(
                    supabase,
                    name="summary",
                    version=SUMMARY_PROMPT_VERSION,
                    prompt_template=CURRENT_SUMMARY_PROMPT,
                    model_name=SUMMARY_MODEL,
                    temperature=SUMMARY_TEMPERATURE,
                    max_tokens=SUMMARY_MAX_TOKENS,
                )
            except Exception as e:
                print(f"ERROR creating/fetching summary prompt: {e}")
                prompt_id = None

            summary = generate_summary(transcript)
            if summary:
                print(f"Summary generated: {summary[:200]}...")
                # Embed the full summary (including hashtags) as a single vector
                try:
                    embedding = generate_embedding_from_summary_text(summary)
                    if embedding:
                        sb = get_supabase()
                        upsert_testimony_embedding(sb, testimony_id, embedding)
                        print(f"Embedded testimony {testimony_id}")
                except Exception as e:
                    print(f"ERROR embedding summary for {testimony_id}: {e}")
            update_db_status(testimony_id, "completed", transcript, summary, summary_prompt_id=prompt_id)
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
