from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Environment, Settings
from app.db.session import get_db
from app.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        APP_ENV=Environment.TEST,
        DEBUG=True,
        LOG_LEVEL="DEBUG",
    )


@pytest.fixture
def mock_db_session() -> AsyncMock:
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def app(test_settings: Settings, mock_db_session: AsyncMock) -> FastAPI:
    application = create_app(settings=test_settings)

    async def override_get_db() -> AsyncGenerator[Any, None]:
        yield mock_db_session

    application.dependency_overrides[get_db] = override_get_db
    return application


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
