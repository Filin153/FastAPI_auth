from common.config import settings
from common.enums import RoleEnum, StatusEnum
from common.interfaces.user import UserInterface
from common.schemas.user import UserCreate, UserUpdate, UserFilters
from common.services.password import Hash
from common.services.send.mail import Mail, CreateMessage, TypeEnum


class FirstAdmin:
    def __init__(self):
        self.mail = Mail()
        self.__email = settings.ADMIN_EMAIL
        self.__password = settings.ADMIN_PASSWORD
        self.user_interface = UserInterface()

    async def init(self):
        old_admin = await self.user_interface.get_all_from_database(UserFilters(**{"role": RoleEnum.ADMIN}), limit=1,
                                                                    with_password=True)
        if not old_admin:
            await self.user_interface.create_in_database(UserCreate(**{
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
                await self.user_interface.update_in_database(UserUpdate(**{
                    "password": self.__password
                }), sub=old_admin.id)

            if old_admin.email != self.__email:
                await self.mail.send_msg(CreateMessage(**{
                    "title": "Смена почты админа",
                    "message": f"Почта админа изменена на -> {self.__email}",
                    "send_to": old_admin.email,
                    "type": TypeEnum.admin,
                }))
                await self.user_interface.update_in_database(UserUpdate(**{
                    "email": self.__email
                }), sub=old_admin.id)
                await self.mail.send_msg(CreateMessage(**{
                    "title": "Акаунт админа перенесен",
                    "message": f"Акаунт админа перенесен на почту -> {self.__email}",
                    "send_to": self.__email,
                    "type": TypeEnum.admin,
                }))
