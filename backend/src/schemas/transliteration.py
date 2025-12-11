# backend/src/schemas/transliteration.py

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class TransliterationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str
    mode: str = "native"  # "native" or "mix"


class TransliterationCandidate(BaseModel):
    text: str
    score: Optional[float] = None


class TransliterationResponse(BaseModel):
    input_text: str
    primary: str
    candidates: List[TransliterationCandidate]
    source_lang: str
    target_lang: str
    mode: str
    provider: str  # e.g. "ml-local", "stub"
