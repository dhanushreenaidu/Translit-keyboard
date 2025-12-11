# backend/src/schemas/stt.py

from typing import Optional
from pydantic import BaseModel


class STTResponse(BaseModel):
    text: str
    provider: str = "stub"


class STTRequest(BaseModel):
    # later this can become real audio upload
    fake_audio_id: Optional[str] = None
