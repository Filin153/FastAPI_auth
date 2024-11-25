from sqlalchemy.orm import Mapped, mapped_column
from .database.database import Base


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(nullable=False, index=True)
    password: Mapped[str] = mapped_column(nullable=False)
    totp_secret: Mapped[str] = mapped_column(nullable=True)