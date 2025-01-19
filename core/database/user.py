from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from core.models.user import UserModel
from core.schemas.user import UserSchemas, UserCreate, UserUpdate
from .database import get_session_async
from ..services.password import Hash



class UserDB:
    async def get(self, filters: dict) -> UserSchemas | None:
        query = select(UserModel).filter_by(**filters)
        async with get_session_async() as session:
            res = await session.execute(query)
            user = res.scalars().one_or_none()
            if user is None:
                return None

        user.password = ""
        return UserSchemas.model_validate(user, from_attributes=True)

    async def update(self, user: UserUpdate) -> bool:
        if user.password:
            user.password = await Hash.get_password_hash(user.password)
        true_user = {key: val for key, val in user.dict() if val}
        user = (update(UserModel)
                .where(UserModel.id == user.id)
                .values(**true_user)
                )

        async with get_session_async() as session:
            try:
                await session.execute(user)
                await session.commit()
                await session.refresh(user)
            except Exception as e:
                raise e
            finally:
                await session.rollback()

        return True

    async def create(self, user: UserCreate) -> bool:
        user.password = await Hash.get_password_hash(user.password)
        user = UserModel(**user.dict())
        async with get_session_async() as session:
            try:
                session.add(user)
                await session.commit()
                await session.refresh(user)
            except IntegrityError:
                raise Exception("User already exists")
            except Exception as e:
                raise e
            finally:
                await session.rollback()

        return True
