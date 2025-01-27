import pyotp
from pydantic import EmailStr

from core.enums import TotpKeyType, QrTypeSaveEnum
from core.schemas.user import UserSchemas
from core.services.fernet import FernetService
from core.services.send.rabbitmq import add_new_msg_task
from core.services.send.schemas import CreateMessage, TypeEnum
import qrcode
import qrcode.image.svg
import io

class TOTPService(FernetService):
    __TEMP_KEY_FOR_VERIFY_EMAIL = {}
    _INTERVAL = 60
    __QR_FACTORY = qrcode.image.svg.SvgImage




    async def send_totp_code(self, user: UserSchemas) -> bool | bytes:
        msg = CreateMessage(
            **{
                "title": "Код для входа!",
                "message": f"Ваш код для входа: {pyotp.TOTP(await self.decrypt_data(user.totp_secret), interval=self._INTERVAL).now()}",
                "send_to": user.email,
                "type": TypeEnum.info,
            }
        )
        await add_new_msg_task(msg)
        return True

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

    async def get_totp_qr_code(self, totp_secret: bytes | str, name: str,
                               type: QrTypeSaveEnum = QrTypeSaveEnum.BYTES, file_name: str = None):
        totp_url = (pyotp.totp.TOTP(await self.decrypt_data(totp_secret), interval=self._INTERVAL)
         .provisioning_uri(name=name, issuer_name='Auth test'))
        img = qrcode.make(totp_url, image_factory=self.__QR_FACTORY)

        if type == QrTypeSaveEnum.SVG and file_name:
            img.save(f'{file_name}.svg')
            return f'{file_name}.svg'
        else:
            byte_io = io.BytesIO()
            img.save(byte_io, format='SVG')
            byte_io.seek(0)
            return byte_io.read()



