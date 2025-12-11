# backend/src/api/health_routes.py

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running"}
