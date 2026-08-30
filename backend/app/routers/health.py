import time
from fastapi import APIRouter
from sqlalchemy import text
from app.schemas.response_schema import APIResponse
from app.utils.db_session import async_session_factory
from app.utils.logger import get_logger

logger = get_logger("routers.health")
router = APIRouter(tags=["Health"])

START_TIME = time.time()


@router.get("/health", response_model=APIResponse[dict])
async def health_check():
    """
    Check API and PostgreSQL database health status.
    """
    db_ok = False
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        logger.error("Health check DB connection failed", error=str(e))

    status_data = {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "uptime_seconds": round(time.time() - START_TIME, 2),
    }

    return APIResponse(
        success=db_ok,
        message="System Operational" if db_ok else "Degraded Service",
        data=status_data,
    )


@router.get("/metrics", response_model=APIResponse[dict])
async def system_metrics():
    """
    Returns basic application runtime metrics.
    """
    return APIResponse(
        success=True,
        message="Metrics fetched",
        data={
            "uptime_seconds": round(time.time() - START_TIME, 2),
            "service": "IDX-Intel AI Bot",
        },
    )
