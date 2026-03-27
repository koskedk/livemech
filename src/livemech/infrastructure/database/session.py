from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from collections.abc import AsyncGenerator

DATABASE_URL = "mysql+asyncmy://root:Password47@localhost:3306/livemech"

engine=create_async_engine(DATABASE_URL,echo=True)

LocalSession=async_sessionmaker (
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db_context()->AsyncGenerator[AsyncSession,None]:
    async with LocalSession() as session:
        yield session