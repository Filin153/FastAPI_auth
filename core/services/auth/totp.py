import os
from enum import Enum

import pyotp
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from pydantic import EmailStr

from core.schemas.user import UserSchemas
from core.services.send.rabbitmq import add_new_msg_task
from core.services.send.schemas import CreateMessage, TypeEnum

load_dotenv()


class TotpKeyType(str, Enum):
    base32 = "base32"
    hex = "hex"


class TOTPService:
    __FERNET_KEY = os.getenv("FERNET_KEY").encode()
    __TEMP_KEY_FOR_VERIFY_EMAIL = {}
    _INTERVAL = 60

    def __init__(self):
        self.__fernet = Fernet(self.__FERNET_KEY)

    async def _encrypt_totp_token(self, data: str) -> bytes:
        return self.__fernet.encrypt(data.encode())

    async def _decrypt_totp_token(self, data: bytes | str) -> str:
        return self.__fernet.decrypt(data).decode()

    async def send_totp_code(self, object_: UserSchemas | EmailStr) -> bool | bytes:
        if isinstance(object_, UserSchemas):
            msg = CreateMessage(
                **{
                    "title": "Код для входа!",
                    "message": f"Ваш код для входа: {pyotp.TOTP(await self._decrypt_totp_token(object_.totp_secret), interval=self._INTERVAL).now()}",
                    "send_to": object_.email,
                    "type": TypeEnum.info,
                }
            )
            await add_new_msg_task(msg)
            return True
        elif isinstance(object_, str) or isinstance(object_, EmailStr):
            tmp_secret = pyotp.random_base32()
            msg = CreateMessage(
                **{
                    "title": "Подтверждение почты",
                    "message": f"Ваш код подтверждения: {pyotp.TOTP(tmp_secret, interval=self._INTERVAL).now()}",
                    "send_to": object_,
                    "type": TypeEnum.info,
                }
            )
            await add_new_msg_task(msg)
            return await self._encrypt_totp_token(tmp_secret)
        else:
            raise TypeError(f"Unsupported object type: {type(object_)}")

    async def get_uniq_totp_secret(self, key_type: TotpKeyType = TotpKeyType.base32) -> bytes:
        if key_type == TotpKeyType.base32:
            totp_secret = pyotp.random_base32()
        elif key_type == TotpKeyType.hex:
            totp_secret = pyotp.random_hex()
        else:
            raise ValueError("Invalid key type")

        return await self._encrypt_totp_token(totp_secret)

    async def verify_totp(self, totp_secret: bytes | str, totp_code: str = None) -> bool:
        totp = pyotp.TOTP(await self._decrypt_totp_token(totp_secret), interval=self._INTERVAL)
        return totp.verify(totp_code)
