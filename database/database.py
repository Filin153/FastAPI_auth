from select import select

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase

from common.config import settings


def get_db_url_async() -> str:
    return f"postgresql+asyncpg://{settings.pg_user}:{settings.pg_pass}@{settings.pg_host}:{settings.pg_port}/{settings.pg_db_name}"


def get_db_url_sync() -> str:
    return f"postgresql://{settings.pg_user}:{settings.pg_pass}@{settings.pg_host}:{settings.pg_port}/{settings.pg_db_name}"


engine_async = create_async_engine(get_db_url_async())
engine_sync = create_engine(get_db_url_sync())


class Base(DeclarativeBase):
    __abstract__ = True

    @classmethod
    def get_query(cls):
        return select(cls).where(cls.delete_at.is_(None))
