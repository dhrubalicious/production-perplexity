from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError

from app.core.config import Settings
from app.core.exceptions import NotFoundError


async def test_liveness(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {}}


async def test_readiness(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"mysql": "ok"}}


async def test_readiness_db_unreachable(
    client: AsyncClient, mock_db_session: AsyncMock
) -> None:
    mock_db_session.execute.side_effect = OperationalError(
        "SELECT 1", {}, Exception("Connection refused")
    )
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "checks": {"mysql": "unavailable"},
    }


async def test_request_id_header_echoed(client: AsyncClient) -> None:
    custom_id = "req-test-12345"
    response = await client.get(
        "/api/v1/health/live", headers={"X-Request-ID": custom_id}
    )
    assert response.headers["X-Request-ID"] == custom_id


async def test_request_id_header_generated(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/live")
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0


async def test_app_error_envelope(app: FastAPI, client: AsyncClient) -> None:
    @app.get("/api/v1/_test-error")
    async def trigger_error() -> None:
        raise NotFoundError("Item missing", details={"item_id": 42})

    response = await client.get("/api/v1/_test-error")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message"] == "Item missing"
    assert body["error"]["details"] == {"item_id": 42}
    assert "request_id" in body["error"]


def test_settings_validation_fails_on_invalid_env() -> None:
    with pytest.raises(ValidationError):
        Settings(APP_ENV="invalid_env")  # type: ignore[arg-type]
