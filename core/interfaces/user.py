from typing import Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.schemas.user import UserCreate, UserSchemas, UserUpdate, UserFilters
from database.interface import BaseDBInterface
from database.models.user import UserModel


class UserInterface(BaseDBInterface):
    def __init__(self):
        super().__init__(UserModel,
                         UserSchemas,
                         UserCreate,
                         UserUpdate,
                         UserFilters)

    async def get_from_database(self, filters: UserFilters, session: Optional[AsyncSession] = None):
        user: UserSchemas = await self._get(filters=filters,
                                            session=session)
        user.password = ""
        return user

    async def get_all_from_database(self, filters: UserFilters = None, limit: int = 10, offset: int = 0, with_password: bool = False,
                                    session: Optional[AsyncSession] = None):
        users: list[UserSchemas] = await self._get_all(filters=filters,
                                                       limit=limit,
                                                       offset=offset,
                                                       session=session)

        if not with_password:
            for user_id in range(len(users)):
                users[user_id].password = ""

        return users

    async def delete(self, sub: Any, model_sub_name: str = "id", session: Optional[AsyncSession] = None):
        return await self._soft_delete(sub=sub,
                                       model_sub_name=model_sub_name,
                                       session=session)

    async def update_in_database(self, update_object: UserUpdate, sub: Any, model_sub_name: str = "id",
                                 session: Optional[AsyncSession] = None):
        return await self._update(update_object=update_object,
                                  sub=sub,
                                  model_sub_name=model_sub_name,
                                  session=session)

    async def create_in_database(self, create_object: UserCreate, session: Optional[AsyncSession] = None):
        return await self._create(create_object=create_object,
                                  session=session)
