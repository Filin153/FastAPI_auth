import asyncio
from typing import Union, Any, Optional

from pydantic import BaseModel
from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from .session import EnginSession


class BaseDBInterface:
    _db_model = None
    _base_schemas = None
    _create_schemas = None
    _update_schemas = None
    _filters_schemas = None

    def __init__(self, db_model: Union[DeclarativeBase, Any],
                 base_schemas: Union[BaseModel, Any],
                 create_schemas: Union[BaseModel, Any],
                 update_schemas: Union[BaseModel, Any],
                 filters_schemas: Union[BaseModel, Any]):
        self._db_model = db_model
        self._base_schemas = base_schemas
        self._create_schemas = create_schemas
        self._update_schemas = update_schemas
        self._filters_schemas = filters_schemas

    async def __query(self, session: AsyncSession, query: Any = None,
                      commit: bool = False, flush: bool = False, begin: bool = False,
                      add_object: _db_model | list[_db_model] = None) -> Any:
        try:
            if begin:
                await session.begin()
            if add_object:
                if isinstance(add_object, list):
                    session.add_all(add_object)
                else:
                    session.add(add_object)

                await session.commit()

                if isinstance(add_object, list):
                    await asyncio.gather(*(session.refresh(obj) for obj in add_object))
                else:
                    await session.refresh(add_object)

                return True
            else:
                res = await session.execute(query)
                if commit:
                    await session.commit()
                if flush:
                    await session.flush()
                return res
        except Exception as e:
            await session.rollback()
            raise e

    async def __do_query(self, session: AsyncSession, query: Any = None,
                         commit: bool = False, flush: bool = False, begin: bool = False,
                         add_object: _db_model = None) -> Any:
        if session:
            res = await self.__query(session, query, commit, flush, begin, add_object)
            return res
        elif not session and (type(query) != type(select)):
            async with EnginSession.get_async() as session:
                res = await self.__query(session, query, commit, flush, begin, add_object)
                return res
        else:
            return None

    async def _get(self, filters: _filters_schemas, session: Optional[AsyncSession] = None) -> Optional[_base_schemas]:
        filters = filters.dict(exclude_unset=True)
        query = select(self._db_model).filter_by(**filters)

        res = await self.__do_query(session, query)
        if not res:
            async with EnginSession.get_async() as session:
                res = await self.__query(session, query)
                response_object = res.scalars().one_or_none()
        else:
            response_object = res.scalars().one_or_none()

        if not response_object:
            return None
        return self._base_schemas.model_validate(response_object, from_attributes=True)

    async def _get_all(self, filters: _filters_schemas = None, limit: int = 10, offset: int = 0,
                       no_limit: bool = False,
                       session: Optional[AsyncSession] = None) -> list[_base_schemas]:

        if no_limit:
            query = select(self._db_model).offset(offset)
        else:
            query = select(self._db_model).offset(offset).limit(limit)


        if filters:
            filters = filters.dict(exclude_unset=True)
            query = query.filter_by(**filters)

        res = await self.__do_query(session, query)
        if not res:
            async with EnginSession.get_async() as session:
                res = await self.__query(session, query)
                response_object = res.scalars().all()
        else:
            response_object = res.scalars().all()

        if not response_object:
            return []
        return [self._base_schemas.model_validate(resp_obj, from_attributes=True) for resp_obj in response_object]

    async def _delete(self, sub: Any = None, model_sub_name: str = "id",
                      filters: dict = None, session: Optional[AsyncSession] = None) -> bool:
        where_filter = []
        if filters:
            for key, value in filters.items():
                model_filed = getattr(self._db_model, key)
                where_filter.append(model_filed == value)
        else:
            model_filed = getattr(self._db_model, model_sub_name)
            where_filter.append(model_filed == sub)

        query = delete(self._db_model).where(and_(*where_filter))

        await self.__do_query(session, query, commit=True)
        return True

    async def _soft_delete(self, sub: Any = None, model_sub_name: str = "id",
                      filters: dict = None, session: Optional[AsyncSession] = None) -> bool:
        where_filter = []
        if filters:
            for key, value in filters.items():
                model_filed = getattr(self._db_model, key)
                where_filter.append(model_filed == value)
        else:
            model_filed = getattr(self._db_model, model_sub_name)
            where_filter.append(model_filed == sub)

        query = update(self._db_model).where(and_(*where_filter)).values({"delete_at": func.now()})

        await self.__do_query(session, query, commit=True)
        return True

    async def _update(self, update_object: _update_schemas, sub: Any, model_sub_name: str = "id",
                      session: Optional[AsyncSession] = None) -> bool:
        true_update_object = update_object.dict(exclude_unset=True)
        model_filed = getattr(self._db_model, model_sub_name)
        query = (update(self._db_model)
                 .where(model_filed == sub)
                 .values(**true_update_object)
                 )
        await self.__do_query(session, query, commit=True, begin=True)
        return True

    async def _create(self, create_object: _create_schemas | list[_create_schemas],
                      session: Optional[AsyncSession] = None) -> bool:
        if isinstance(create_object, list):
            add_object = [self._db_model(**obj.dict()) for obj in create_object]
        else:
            add_object = self._db_model(**create_object.dict())

        await self.__do_query(session, add_object=add_object)
        return True
