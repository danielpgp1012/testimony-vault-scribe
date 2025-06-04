from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel


class ChurchLocation(str, Enum):
    LAUSANNE = "Lausanne"
    ZURICH = "Zurich"
    BERN = "Bern"
    GINEBRA = "Ginebra"
    US = "US"


class TestimonyBase(BaseModel):
    # title: str
    church_id: Optional[ChurchLocation] = ChurchLocation.LAUSANNE

    # date: date
    tags: List[str] = []


class TestimonyCreate(TestimonyBase):
    pass


class TestimonyOut(TestimonyBase):
    id: Union[int, str]  # Support both int and str to handle existing data
    transcript_status: str
    transcript: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    recorded_at: Optional[date] = None

    # Audio metadata fields
    audio_hash: Optional[str] = None
    audio_duration_ms: Optional[int] = None
    user_file_name: Optional[str] = None


class ProfileOut(BaseModel):
    id: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    updated_at: datetime
