from enum import Enum

from pydantic import BaseModel


class TypeEnum(str, Enum):
    admin = 'admin'
    info = 'info'


class CreateMessage(BaseModel):
    title: str
    message: str
    send_to: str
    type: TypeEnum
