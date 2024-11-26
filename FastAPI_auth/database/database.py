from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from contextlib import asynccontextmanager

engine = create_async_engine("sqlite+aiosqlite:///./auth_test.db")

class Base(DeclarativeBase):
    pass

@asynccontextmanager
async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as conn:
        yield conn



