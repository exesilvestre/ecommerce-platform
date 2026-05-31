from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

_engine: AsyncEngine | None = None
_SessionFactory: async_sessionmaker[AsyncSession] | None = None


class Base(DeclarativeBase):
    pass


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(settings.database_url)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _SessionFactory


async def get_db():
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
