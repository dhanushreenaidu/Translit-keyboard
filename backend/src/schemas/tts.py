# backend/src/schemas/tts.py

from pydantic import BaseModel


class TTSRequest(BaseModel):
    text: str
    lang: str = "en"  # e.g. "hi", "te" etc.
