# backend/src/api/language_routes.py

from fastapi import APIRouter

from ..schemas.language import LanguageDetectRequest, LanguageDetectResponse
from ..services.language_service import language_service

router = APIRouter(prefix="/detect-language", tags=["language"])


@router.post("", response_model=LanguageDetectResponse)
async def detect_language(req: LanguageDetectRequest) -> LanguageDetectResponse:
    """
    Heuristic language detection based on Unicode script ranges:

    - Latin only -> "en"
    - Single Indic script -> "hi", "te", "ta", "kn", "ml", etc.
    - Mixed Latin + Indic -> main Indic language or "mixed"
    """
    return language_service.detect(req)
