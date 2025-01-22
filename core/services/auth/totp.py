import pyotp
from pydantic import EmailStr

from core.enums import TotpKeyType
from core.schemas.user import UserSchemas
from core.services.fernet import FernetService
from core.services.send.rabbitmq import add_new_msg_task
from core.services.send.schemas import CreateMessage, TypeEnum


class TOTPService(FernetService):
    __TEMP_KEY_FOR_VERIFY_EMAIL = {}
    _INTERVAL = 60

    async def send_totp_code(self, object_: UserSchemas | EmailStr) -> bool | bytes:
        if isinstance(object_, UserSchemas):
            msg = CreateMessage(
                **{
                    "title": "Код для входа!",
                    "message": f"Ваш код для входа: {pyotp.TOTP(await self.decrypt_data(object_.totp_secret), interval=self._INTERVAL).now()}",
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
            return await self.encrypt_data(tmp_secret)
        else:
            raise TypeError(f"Unsupported object type: {type(object_)}")

    async def get_uniq_totp_secret(self, key_type: TotpKeyType = TotpKeyType.base32) -> bytes:
        if key_type == TotpKeyType.base32:
            totp_secret = pyotp.random_base32()
        elif key_type == TotpKeyType.hex:
            totp_secret = pyotp.random_hex()
        else:
            raise ValueError("Invalid key type")

        return await self.encrypt_data(totp_secret)

    async def verify_totp(self, totp_secret: bytes | str, totp_code: str = None) -> bool:
        totp = pyotp.TOTP(await self.decrypt_data(totp_secret), interval=self._INTERVAL)
        return totp.verify(totp_code)
