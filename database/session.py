from contextlib import asynccontextmanager, contextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .database import engine_sync, engine_async


class EnginSession:

    @staticmethod
    @asynccontextmanager
    async def get_async() -> AsyncSession:
        async with AsyncSession(engine_async) as conn:
            yield conn

    @staticmethod
    @contextmanager
    def get_sync() -> Session:
        with Session(engine_sync) as conn:
            yield conn
