# backend/src/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config.settings import settings

from .api.health_routes import router as health_router
from .api.transliteration_routes import router as transliteration_router
from .api.language_routes import router as language_router
from .api.tts_routes import router as tts_router
from .api.stt_routes import router as stt_router
from .api.chat_routes import router as chat_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)

    origins = settings.BACKEND_CORS_ORIGINS

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    app.include_router(health_router, prefix=settings.API_PREFIX)
    app.include_router(transliteration_router, prefix=settings.API_PREFIX)
    app.include_router(language_router, prefix=settings.API_PREFIX)
    app.include_router(tts_router, prefix=settings.API_PREFIX)
    app.include_router(stt_router, prefix=settings.API_PREFIX)
    app.include_router(chat_router, prefix=settings.API_PREFIX)

    @app.get("/")
    async def root():
        return {"message": "TransKey ML Backend running. See /api/health"}

    return app


app = create_app()
