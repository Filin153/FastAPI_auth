from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class UserSchemas(BaseModel):
    username: str
    password: str
    totp_secret: str | None