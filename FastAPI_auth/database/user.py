from watchfiles import awatch

from FastAPI_auth.models import UserModel
from FastAPI_auth.schemas import UserSchemas
from .database import get_session
from sqlalchemy import select

class UserDB:
    async def get(self, filters: dict):
        query = select(UserModel).filter_by(**filters)
        async with get_session() as session:
            res = await session.execute(query)
            user = res.scalars().one_or_none()
            if user is None:
                return None
            return UserSchemas.model_validate(user, from_attributes=True)

