# backend/src/api/transliteration_routes.py

from fastapi import APIRouter

from ..schemas.transliteration import TransliterationRequest, TransliterationResponse
from ..services.transliteration_service import transliteration_service

router = APIRouter(prefix="/transliterate", tags=["transliteration"])


@router.post("", response_model=TransliterationResponse)
async def transliterate(req: TransliterationRequest) -> TransliterationResponse:
    return transliteration_service.transliterate(req)
