# backend/src/schemas/chat.py

from typing import List, Literal
from pydantic import BaseModel

RoleType = Literal["user", "assistant"]


class ChatMessage(BaseModel):
    role: RoleType
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    language: str = "en"  # "hi", "te", etc.


class ChatResponse(BaseModel):
    reply: str
    provider: str = "stub"
