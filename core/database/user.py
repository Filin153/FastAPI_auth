from core.models.user import UserModel
from core.schemas.user import UserSchemas
from .database import get_session_async
from sqlalchemy import select


class UserDB:
    async def get(self, filters: dict):
        query = select(UserModel).filter_by(**filters)
        async with get_session_async() as session:
            res = await session.execute(query)
            user = res.scalars().one_or_none()
            if user is None:
                return None

        return UserSchemas.model_validate(user, from_attributes=True)

    async def create(self, user: UserSchemas):
        user = UserModel(**user.dict())
        async with get_session_async() as session:
            try:
                session.add(user)
                await session.commit()
                await session.refresh(user)
            except Exception as e:
                await session.rollback()
                raise e

        return True


