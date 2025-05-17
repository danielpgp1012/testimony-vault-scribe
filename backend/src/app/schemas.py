from typing import List, Optional
from datetime import date, datetime

from pydantic import BaseModel

class TestimonyBase(BaseModel):
    # title: str
    church_id: Optional[str] = None

    # date: date
    tags: List[str] = []

class TestimonyCreate(TestimonyBase):
    pass

class TestimonyOut(TestimonyBase):
    id: int
    storage_url: Optional[str] = None
    transcript_status: str
    transcript: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Audio metadata fields
    audio_hash: Optional[str] = None
    audio_duration_ms: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
