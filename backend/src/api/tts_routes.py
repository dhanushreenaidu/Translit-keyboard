# backend/src/api/tts_routes.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..schemas.tts import TTSRequest
from ..services.tts_service import tts_service

router = APIRouter(prefix="/tts", tags=["tts"])


@router.post("", response_class=FileResponse)
async def tts_endpoint(req: TTSRequest):
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        out_path = tts_service.synthesize_to_file(text, req.lang)
    except Exception as e:
        print(f"[TTS] Error: {e}")
        raise HTTPException(status_code=500, detail="TTS synthesis failed")

    return FileResponse(
        path=out_path,
        media_type="audio/wav",
        filename=out_path.name,
    )
