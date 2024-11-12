import os
from typing import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()

host = os.getenv("POSTGRES_HOST", "localhost")
user = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "root")
port = os.getenv("POSTGRES_PORT", "5432")
name = os.getenv("POSTGRES_DB", "fastapi")

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{user}:{password}@{host}:{port}/"


async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL + name, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db
