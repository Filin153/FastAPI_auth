from enum import Enum

from pydantic import BaseModel, EmailStr


class TypeEnum(str, Enum):
    admin = 'admin'
    info = 'info'


class CreateMessage(BaseModel):
    title: str
    message: str
    send_to: EmailStr
    type: TypeEnum
