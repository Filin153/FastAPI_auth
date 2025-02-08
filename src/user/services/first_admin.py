from core.config import settings
from core.database.user import UserDB
from core.enums import RoleEnum, StatusEnum
from core.schemas.user import UserCreate, UserUpdate
from core.services.password import Hash
from core.services.send.mail import Mail, CreateMessage, TypeEnum


class FirstAdmin:
    def __init__(self):
        self.mail = Mail()
        self.__email = settings.ADMIN_EMAIL
        self.__password = settings.ADMIN_PASSWORD
        self.user_db = UserDB()

    async def init(self):
        old_admin = await self.user_db.get_all({"role": RoleEnum.ADMIN}, limit=1, with_password=True)
        if not old_admin:
            await self.user_db.create(UserCreate(**{
                "email": self.__email,
                "password": self.__password,
                "role": RoleEnum.ADMIN,
                "status": StatusEnum.ACTIVE,
            }))
            await self.mail.send_msg(CreateMessage(**{
                "title": "Акаунт админа создан",
                "message": "Акаунт админа создан!",
                "send_to": self.__email,
                "type": TypeEnum.admin,
            }))
        else:
            old_admin = old_admin[0]
            if not await Hash.verify_password(self.__password, old_admin.password):
                await self.user_db.update(UserUpdate(**{
                    "id": old_admin.id,
                    "password": self.__password
                }, exclude_unset=True))

            if old_admin.email != self.__email:
                await self.mail.send_msg(CreateMessage(**{
                    "title": "Смена почты админа",
                    "message": f"Почта админа изменена на -> {self.__email}",
                    "send_to": old_admin.email,
                    "type": TypeEnum.admin,
                }))
                await self.user_db.update(UserUpdate(**{
                    "id": old_admin.id,
                    "email": self.__email
                }, exclude_unset=True))
                await self.mail.send_msg(CreateMessage(**{
                    "title": "Акаунт админа перенесен",
                    "message": f"Акаунт админа перенесен на почту -> {self.__email}",
                    "send_to": self.__email,
                    "type": TypeEnum.admin,
                }))
