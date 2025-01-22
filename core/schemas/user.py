from pydantic import BaseModel, EmailStr, Extra
from core.enums import RoleEnum, StatusEnum

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    class Config:
        extra = Extra.allow

class UserUpdate(BaseModel):
    id: int
    username: str | None
    email: EmailStr | None
    password: str | None
    totp_secret: bytes | None
    role: RoleEnum | None
    status: StatusEnum | None

class UserAuthData(BaseModel):
    email: EmailStr
    password: str
    totp_code: str

class UserSchemas(UserCreate):
    id: int
    role: RoleEnum
    totp_secret: bytes
    status: StatusEnum
