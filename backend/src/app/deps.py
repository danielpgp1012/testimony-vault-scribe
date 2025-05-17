import os
from functools import lru_cache
from supabase import create_client, Client
from google.cloud import storage

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
SERVICE_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

@lru_cache
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@lru_cache
def get_gcs_client():
    """Returns a Google Cloud Storage client."""
    # First check if credentials are available through environment
    try:
        return storage.Client()
    except Exception:
        # Fall back to service account JSON file if specified
        if not SERVICE_JSON:
            raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS env not set")
        return storage.Client.from_service_account_json(SERVICE_JSON)

if __name__ == "__main__":
    print(get_supabase())
    print(get_gcs_client())
    a=1
