from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings, get_settings


def create_engine(settings: Settings | None = None) -> AsyncEngine:
    active = settings or get_settings()
    return create_async_engine(
        active.DATABASE_URL,
        pool_size=active.DB_POOL_SIZE,
        max_overflow=active.DB_MAX_OVERFLOW,
        pool_recycle=active.DB_POOL_RECYCLE,
        pool_pre_ping=True,
        echo=active.DB_ECHO,
    )


engine: AsyncEngine = create_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
