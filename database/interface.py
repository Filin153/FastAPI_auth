from typing import Union, Any, Optional

from pydantic import BaseModel
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from .session import EnginSession


class BaseDBInterface:
    _db_model = None
    _base_schemas = None
    _create_schemas = None
    _update_schemas = None
    _filters_schemas = None

    def __init__(self, db_model: DeclarativeBase, base_schemas: Union[BaseModel, Any],
                 create_schemas: Union[BaseModel, Any], update_schemas: Union[BaseModel, Any],
                 filters_schemas: Union[BaseModel, Any]):
        self._db_model = db_model
        self._base_schemas = base_schemas
        self._create_schemas = create_schemas
        self._update_schemas = update_schemas
        self._filters_schemas = filters_schemas

    async def __query(self, session: AsyncSession, query: Any = None,
                      commit: bool = False, flush: bool = False, begin: bool = False,
                      add_object: _create_schemas = None) -> Any:
        try:
            if begin:
                await session.begin()
            if add_object:
                session.add(self._db_model)
                await session.commit()
                await session.refresh(add_object)
            else:
                res = await session.execute(query)
                if commit:
                    await session.commit()
                if flush:
                    await session.flush()
        except Exception as e:
            raise e
        finally:
            await session.rollback()

        return res

    async def __do_query(self, session: AsyncSession, query: Any = None,
                         commit: bool = False, flush: bool = False, begin: bool = False,
                         add_object: _create_schemas = None) -> Any:
        if session:
            res = await self.__query(query, session, commit, flush, begin, add_object)
        else:
            async with EnginSession.get_async() as session:
                res = await self.__query(query, session, commit, flush, begin, add_object)
        return res

    async def get(self, filters: _filters_schemas, session: Optional[AsyncSession] = None) -> Optional[_base_schemas]:
        filters = filters.dict(exclude_unset=True)
        query = select(self._db_model).filter_by(**filters)
        res = await self.__do_query(session, query)
        response_object = res.scalars().one_or_none()
        if response_object is None:
            return None
        return self._base_schemas.model_validate(response_object, from_attributes=True)

    async def get_all(self, filters: _filters_schemas = None, limit: int = 10, offset: int = 0,
                      session: Optional[AsyncSession] = None) -> list[_base_schemas]:
        query = select(self._db_model).offset(offset).limit(limit)

        if filters:
            filters = filters.dict(exclude_unset=True)
            query = query.filter_by(**filters)

        res = await self.__do_query(session, query)
        response_object = res.scalars().all()
        if response_object is None:
            return []
        return [self._base_schemas.model_validate(resp_obj, from_attributes=True) for resp_obj in response_object]

    async def delete(self, sub: Any, model_sub_name: str = "id", session: Optional[AsyncSession] = None) -> bool:
        model_filed = getattr(self._db_model, model_sub_name)
        query = delete(self._db_model).where(model_filed == sub)
        await self.__do_query(session, query, commit=True)
        return True

    async def soft_delete(self, sub: Any, model_sub_name: str = "id", session: Optional[AsyncSession] = None) -> bool:
        model_filed = getattr(self._db_model, model_sub_name)
        query = update(self._db_model).where(model_filed == sub).values({"delete_at": func.now()})
        await self.__do_query(session, query, commit=True)
        return True

    async def update(self, update_object: _update_schemas, sub: Any, model_sub_name: str = "id",
                     session: Optional[AsyncSession] = None) -> bool:
        true_update_object = update_object.dict(exclude_unset=True)
        model_filed = getattr(self._db_model, model_sub_name)
        query = (update(self._db_model)
                 .where(model_filed == sub)
                 .values(**true_update_object)
                 )
        await self.__do_query(session, query, commit=True, begin=True)
        return True

    async def create(self, create_object: _create_schemas, session: Optional[AsyncSession] = None) -> bool:
        add_object = self._db_model(**create_object.dict())
        await self.__do_query(session, add_object=add_object)
        return True
