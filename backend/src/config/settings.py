from pydantic_settings import BaseSettings
from typing import Union


class Settings(BaseSettings):
    APP_NAME: str = "TransKey ML Backend"
    API_PREFIX: str = "/api"

    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # 👇 point to project-root/data/models
    MODEL_DIR: str = "../data/models"

    # 🔹 Gemini integration
    GEMINI_API_KEY: Union[str, None] = None
    CHAT_PROVIDER: str = "gemini"

    class Config:
        env_file = ".env"


settings = Settings()
