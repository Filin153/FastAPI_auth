from sqlalchemy.orm import Mapped, mapped_column
from core.database.database import Base
from sqlalchemy import Enum
from pydantic import EmailStr
from core.enums import RoleEnum


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(nullable=False, index=True, unique=True)
    email: Mapped[str] = mapped_column(index=True, unique=True)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum, name="role_enum"), nullable=False, default=RoleEnum.USER)
    password: Mapped[str] = mapped_column(nullable=False)
