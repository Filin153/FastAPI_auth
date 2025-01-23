
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session, as_declarative
from contextlib import asynccontextmanager, contextmanager
from .config import *



engine_async = create_async_engine(get_db_url_async())
engine_sync = create_engine(get_db_url_sync())

@as_declarative()
class Base(DeclarativeBase):
    __abstract__ = True

    @classmethod
    def get_query(cls):
        return select(cls).where(cls.delete_at.is_(None))

@asynccontextmanager
async def get_session_async() -> AsyncSession:
    async with AsyncSession(engine_async) as conn:
        yield conn

@contextmanager
def get_session_sync() -> Session:
    with Session(engine_sync) as conn:
        yield conn


