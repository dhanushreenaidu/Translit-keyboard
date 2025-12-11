from pydantic import BaseModel


class LanguageDetectionRequest(BaseModel):
    text: str


class LanguageDetectionResponse(BaseModel):
    text: str
    language: str
    confidence: float
    is_mixed: bool = False
