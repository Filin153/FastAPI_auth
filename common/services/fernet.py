import json

from cryptography.fernet import Fernet

from common.config import settings


class FernetService:
    __FERNET_KEY = settings.FERNET_KEY.encode()

    def __init__(self):
        self.__fernet = Fernet(self.__FERNET_KEY)

    async def encrypt_data(self, data: str | dict, to_json: bool = False) -> bytes:
        if to_json:
            return self.__fernet.encrypt(json.dumps(data).encode())
        else:
            return self.__fernet.encrypt(data.encode())

    async def decrypt_data(self, data: bytes | str, to_json: bool = False) -> str:
        if to_json:
            return json.loads(self.__fernet.decrypt(data).decode())
        else:
            return self.__fernet.decrypt(data).decode()
