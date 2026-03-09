from fastapi import APIRouter
from datetime import datetime
import sys

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }


@router.get("/api/v1/system/status")
async def system_status():
    return {
        "status": "running",
        "python": sys.version,
        "timestamp": datetime.utcnow().isoformat(),
    }
