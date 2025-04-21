
import os, time, requests
from celery import Celery
from google.cloud import speech_v1p1beta1 as speech
from supabase import create_client
from .crud import update_testimony

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

celery = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)
sb = create_client(SUPABASE_URL, SUPABASE_KEY)
speech_client = speech.SpeechClient()

@celery.task(bind=True, max_retries=3)
def transcribe_testimony(self, testimony_id: int, audio_url: str):
    try:
        update_testimony(sb, testimony_id, {"transcript_status": "processing"})
        # Download audio bytes (Supabase Storage signed/public url)
        audio_bytes = requests.get(audio_url, timeout=120).content

        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
            language_code="es-ES",
            enable_automatic_punctuation=True,
        )

        operation = speech_client.long_running_recognize(config=config, audio=audio)
        response = operation.result(timeout=900)

        transcript = "\n".join(
            alt.transcript for res in response.results for alt in res.alternatives
        )

        update_testimony(
            sb,
            testimony_id,
            {"transcript_status": "completed", "transcript": transcript},
        )
    except Exception as exc:
        update_testimony(sb, testimony_id, {"transcript_status": "failed"})
        raise self.retry(exc=exc, countdown=60)
