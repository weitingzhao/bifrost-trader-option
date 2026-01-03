"""Health check route."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import logging

from src.config import config
from src.core.connector.ib import get_connector

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        connector = await get_connector()
        is_connected = connector.is_connected()
        
        return {
            "status": "healthy" if is_connected else "degraded",
            "ib_connected": is_connected,
            "ib_host": config.IB_HOST,
            "ib_port": config.IB_PORT
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

