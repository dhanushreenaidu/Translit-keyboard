# backend/src/schemas/language.py

from pydantic import BaseModel


class LanguageDetectRequest(BaseModel):
    text: str


class LanguageDetectResponse(BaseModel):
    text: str
    language: str  # e.g. "hi", "te", "ta", "en", "mixed", "unknown"
    script: str  # e.g. "devanagari", "telugu", "latin", "latin+telugu"
    confidence: float
