import os

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = os.environ["DATABASE_URL"]

engine=create_async_engine(DATABASE_URL,echo=True)

LocalSession=async_sessionmaker (
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db_context()->AsyncGenerator[AsyncSession,None]:
    async with LocalSession() as session:
        yield session