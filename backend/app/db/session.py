from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession


engine = create_async_engine(settings.database_url)
AsyncSessionFactory = sessionmaker(engine, class = AsyncSession)


class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionFactory() as session:
        yield session

