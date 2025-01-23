import os

from dotenv import load_dotenv

from core.database.user import UserDB
from core.enums import RoleEnum, StatusEnum
from core.schemas.user import UserCreate, UserUpdate
from core.services.password import Hash
from core.services.send import send_msg, CreateMessage
from core.services.send.schemas import TypeEnum

load_dotenv()


class FirstAdmin:
    def __init__(self):
        self.__email = os.getenv("ADMIN_EMAIL")
        self.__password = os.getenv("ADMIN_PASSWORD")
        self.user_db = UserDB()

    async def init(self):
        old_admin = await self.user_db.get_all({"role": RoleEnum.ADMIN}, limit=1)
        if not old_admin:
            await self.user_db.create(UserCreate(**{
                "username": "Admin",
                "email": self.__email,
                "password": self.__password,
                "role": RoleEnum.ADMIN,
                "status": StatusEnum.ACTIVE,
            }))
            await send_msg(CreateMessage(**{
                "title": "Акаунт админа создан",
                "message": "Акаунт админа создан!",
                "send_to": self.__email,
                "type": TypeEnum.admin,
            }))

        old_admin = old_admin[0]
        if not Hash.verify_password(self.__password, old_admin.password):
            await self.user_db.update(UserUpdate(**{
                "id": old_admin.id,
                "password": self.__password
            }))

        if old_admin.email != self.__email:
            await send_msg(CreateMessage(**{
                "title": "Смена почты админа",
                "message": f"Почта админа изменена на -> {self.__email}",
                "send_to": old_admin.email,
                "type": TypeEnum.admin,
            }))
            await self.user_db.update(UserUpdate(**{
                "id": old_admin.id,
                "email": self.__email
            }))
            await send_msg(CreateMessage(**{
                "title": "Акаунт админа перенесен",
                "message": f"Акаунт админа перенесен на почту -> {self.__email}",
                "send_to": self.__email,
                "type": TypeEnum.admin,
            }))
