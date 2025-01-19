from pydantic import BaseModel, EmailStr
from core.enums import RoleEnum

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserAuthData(BaseModel):
    username: str | None
    email: EmailStr | None
    password: str

class UserSchemas(UserCreate):
    id: int
    role: RoleEnum
