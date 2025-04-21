
import os
from functools import lru_cache
from supabase import create_client, Client
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from google.cloud import storage

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
SERVICE_JSON = os.getenv("GDRIVE_SERVICE_JSON")

@lru_cache
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@lru_cache
def get_drive():
    if not SERVICE_JSON:
        raise RuntimeError("GDRIVE_SERVICE_JSON env not set")
    creds = Credentials.from_service_account_file(
        SERVICE_JSON, scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)

@lru_cache
def get_gcs_client():
    if not SERVICE_JSON:
        raise RuntimeError("GDRIVE_SERVICE_JSON env not set")
    return storage.Client.from_service_account_json(SERVICE_JSON)
