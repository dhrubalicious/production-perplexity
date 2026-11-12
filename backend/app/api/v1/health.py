from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.deps import DbSessionDep
from app.core.logging import get_logger
from app.schemas.common import HealthResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=HealthResponse)
async def liveness() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/ready", response_model=HealthResponse)
async def readiness(db: DbSessionDep) -> HealthResponse | JSONResponse:
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.warning("health.readiness.db_failed", error=str(exc))
        payload = HealthResponse(status="degraded", checks={"mysql": "unavailable"})
        return JSONResponse(status_code=503, content=payload.model_dump())
    return HealthResponse(status="ok", checks={"mysql": "ok"})
