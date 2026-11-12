from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.exceptions import AppError
from app.core.logging import get_logger, request_id_ctx, setup_logging
from app.core.middleware import RequestContextMiddleware
from app.schemas.common import ErrorDetail, ErrorEnvelope

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(
        log_level=settings.LOG_LEVEL,
        json_logs=settings.APP_ENV not in ("local", "test"),
    )
    logger.info("app.startup", app_name=settings.APP_NAME, env=settings.APP_ENV)
    yield
    logger.info("app.shutdown")


def create_app(settings: Settings | None = None) -> FastAPI:
    active_settings = settings or get_settings()
    app = FastAPI(
        title=active_settings.APP_NAME,
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=active_settings.ALLOWED_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: Exception) -> JSONResponse:
        assert isinstance(exc, AppError)
        envelope = ErrorEnvelope(
            error=ErrorDetail(
                code=exc.code,
                message=exc.message,
                request_id=request_id_ctx.get(),
                details=exc.details,
            )
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=envelope.model_dump(exclude_none=True),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled.exception", error=str(exc))
        envelope = ErrorEnvelope(
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message="An unexpected internal error occurred.",
                request_id=request_id_ctx.get(),
            )
        )
        return JSONResponse(
            status_code=500,
            content=envelope.model_dump(exclude_none=True),
        )

    app.include_router(api_router)

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"status": "ok", "service": "production-perplexity-backend"}

    return app


app = create_app()
