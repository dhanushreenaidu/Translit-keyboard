# backend/src/api/stt_routes.py

from fastapi import APIRouter

from ..schemas.stt import STTRequest, STTResponse

router = APIRouter(prefix="/stt", tags=["stt"])


@router.post("", response_model=STTResponse)
async def stt(_: STTRequest) -> STTResponse:
    """
    Phase 2 stub:
    - Later, this will accept audio and run offline STT.
    - For now, just return a fixed sentence.
    """
    return STTResponse(
        text="(STT stub) This is where recognized speech text will appear.",
        provider="stub",
    )
