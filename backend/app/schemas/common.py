from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str | None = None
    details: dict[str, Any] | None = None


class ErrorEnvelope(BaseModel):
    error: ErrorDetail


class HealthResponse(BaseModel):
    status: str
    checks: dict[str, str] = Field(default_factory=dict)


class PaginationParams(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    cursor: str | None = None


class PaginatedResponse[T](BaseModel):
    items: list[T]
    next_cursor: str | None = None
    has_more: bool = False
