from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    totp_secret: str | None

class UserSchemas(UserCreate):
    id: int