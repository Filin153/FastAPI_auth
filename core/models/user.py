from datetime import datetime
from typing import Union

from sqlalchemy import Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database.database import Base
from core.enums import RoleEnum, StatusEnum

# TODO Delete username from all
# TODO Checker for old INACTIVE user and delete they
# TODO Make new revision
class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(nullable=False)

    email: Mapped[str] = mapped_column(index=True, unique=True)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum, name="role_enum"), nullable=False, default=RoleEnum.USER)
    status: Mapped[RoleEnum] = mapped_column(Enum(StatusEnum, name="status_enum"), nullable=False, default=StatusEnum.INACTIVE)
    password: Mapped[str] = mapped_column(nullable=False)
    totp_secret: Mapped[bytes] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    delete_at: Mapped[Union[datetime, None]] = mapped_column(DateTime(timezone=True), nullable=True)
