from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import IntegrityError

from core.models.user import UserModel
from core.schemas.user import UserSchemas, UserCreate, UserUpdate
from core.services.password import Hash
from .database import get_session_async


class UserDB:
    async def get(self, filters: dict) -> UserSchemas | None:
        query = select(UserModel).filter_by(**filters)
        async with get_session_async() as session:
            res = await session.execute(query)
            user = res.scalars().one_or_none()
            if user is None:
                return None

        return UserSchemas.model_validate(user, from_attributes=True)

    async def get_all(self, filters: dict, limit: int = 100, offset: int = 0, with_password: bool = False) -> list[UserSchemas]:
        query = select(UserModel).offset(offset).limit(limit)
        if filters:
            query = query.filter_by(**filters)

        async with get_session_async() as session:
            res = await session.execute(query)
            users = res.scalars().all()
            if users is None:
                return []

        if not with_password:
            for id_user, _ in enumerate(users):
                users[id_user].password = ""

        return [UserSchemas.model_validate(user, from_attributes=True) for user in users]

    async def delete(self, id: int) -> bool:
        query = delete(UserModel).where(UserModel.id == id)
        async with get_session_async() as session:
            try:
                await session.execute(query)
                await session.commit()
            except Exception as e:
                raise e
            finally:
                await session.rollback()

        return True

    async def soft_delete(self, id: int) -> bool:
        query = update(UserModel).where(UserModel.id == id).values({"delete_at": func.now()})
        async with get_session_async() as session:
            try:
                await session.execute(query)
                await session.commit()
            except Exception as e:
                raise e
            finally:
                await session.rollback()

        return True

    async def update(self, user: UserUpdate) -> bool:
        if user.password:
            user.password = await Hash.get_password_hash(user.password)
        true_user = user.dict(exclude_unset=True)
        user = (update(UserModel)
                .where(UserModel.id == user.id)
                .values(**true_user)
                )

        async with get_session_async() as session:
            try:
                await session.begin()
                await session.execute(user)
                await session.commit()
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
