# backend/src/api/chat_routes.py

from fastapi import APIRouter

from ..schemas.chat import ChatRequest, ChatResponse
from ..services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest) -> ChatResponse:
    # generate_reply is sync; FastAPI will handle this fine
    return chat_service.generate_reply(req)
