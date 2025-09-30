from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from ..core.config import settings


engine: AsyncEngine = create_async_engine(
    settings.sqlalchemy_database_uri,
    echo=settings.db_echo,
    future=True,
)

AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with AsyncSessionFactory() as session:  # pragma: no cover - dependency wiring
        yield session
