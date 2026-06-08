from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .common import SQLALCHEMY_DATABASE_URL, name, ssl_mode

async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL + name, pool_pre_ping=True, connect_args={"sslmode": ssl_mode}
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db
