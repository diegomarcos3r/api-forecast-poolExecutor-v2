from fastapi import APIRouter
from typing import Dict

health_router = APIRouter(prefix="/health", tags=["health"])

@health_router.get("/live")
async def health_check() -> dict:
    return {"Status": "API rodando na porta 8000 do host."}