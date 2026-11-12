from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.base import Base
from app.models.user import User
from app.repositories.user_repository import UserRepository


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    settings = get_settings()
    engine = create_async_engine(settings.TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session
        await session.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


async def test_user_repository_crud_and_unique_email(
    db_session: AsyncSession,
) -> None:
    repo = UserRepository(db_session)
    user = User(email="dhrub@example.com", password_hash="hashed_secret")
    created = await repo.add(user)

    assert created.id is not None
    assert await repo.email_exists("DHRUB@example.com") is True

    fetched = await repo.get_by_email("dhrub@example.com")
    assert fetched is not None
    assert fetched.id == created.id

    duplicate = User(email="dhrub@example.com", password_hash="other_hash")
    with pytest.raises(IntegrityError):
        await repo.add(duplicate)
    await db_session.rollback()
