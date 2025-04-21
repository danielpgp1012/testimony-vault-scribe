
from typing import List, Optional
from datetime import date, datetime

from pydantic import BaseModel

class TestimonyBase(BaseModel):
    title: str
    speaker: Optional[str] = None
    date: date
    tags: List[str] = []

class TestimonyCreate(TestimonyBase):
    pass

class TestimonyOut(TestimonyBase):
    id: int
    drive_id: Optional[str] = None
    storage_url: Optional[str] = None
    transcript_status: str
    transcript: Optional[str] = None
    created_at: datetime
    updated_at: datetime
