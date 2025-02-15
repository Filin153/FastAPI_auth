from cryptography.fernet import Fernet

from common.config import settings


class FernetService:
    __FERNET_KEY = settings.FERNET_KEY.encode()

    def __init__(self):
        self.__fernet = Fernet(self.__FERNET_KEY)

    async def encrypt_data(self, data: str) -> bytes:
        return self.__fernet.encrypt(data.encode())

    async def decrypt_data(self, data: bytes | str) -> str:
        return self.__fernet.decrypt(data).decode()
