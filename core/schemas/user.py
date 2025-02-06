from pydantic import BaseModel, EmailStr, Extra

from core.enums import RoleEnum, StatusEnum


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    class Config:
        extra = Extra.allow


class UserUpdate(BaseModel):
    id: int | None = None
    email: EmailStr | None = None
    password: str | None = None
    totp_secret: bytes | None = None
    role: RoleEnum | None = None
    status: StatusEnum | None = None


class UserAuthData(BaseModel):
    email: EmailStr
    password: str
    totp_code: str | None = None


class UserSchemas(UserCreate):
    id: int
    role: RoleEnum
    totp_secret: bytes | None = None
    status: StatusEnum
