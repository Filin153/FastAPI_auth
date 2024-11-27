from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
import pyotp
from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from .excepts import *
from core.schemas.user import UserSchemas

# URL для получения токена
tokenUrl = "/token"


class TwoFAuth:
    # Метод для генерации нового секретного ключа для TOTP
    async def get_new_totp_secret_key(self):
        secret_key = pyotp.random_base32()  # Генерация случайного секретного ключа
        return secret_key

    # Метод для получения текущего TOTP-кода на основе секретного ключа
    async def get_totp_code(self, secret_key: str):
        return pyotp.TOTP(secret_key).now()  # Генерация текущего одноразового пароля на основе ключа

    async def get_totp_url(self, secret_key: str, name: str):
        return pyotp.totp.TOTP(secret_key).provisioning_uri(
            name=name,  # Имя пользователя, которое будет отображаться в приложении 2FA
            issuer_name='Goose App'  # Название приложения или сервиса, который использует 2FA
        )

    # Метод для верификации TOTP-кода, введённого пользователем
    async def verify_totp_code(self, secret_key: str, user_code: str) -> bool:
        totp = pyotp.TOTP(secret_key)
        if totp.now() != user_code:  # Сравнение с текущим сгенерированным кодом
            raise Exception("Invalid TOTP token")  # Выбрасывание исключения в случае несовпадения
        return True  # Возвращаем True, если код верный

# Класс для работы с хешированием паролей
class Hash:
    # Контекст для работы с хешированием паролей с использованием bcrypt
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    # Метод для верификации пароля: сравнение plain-текста с хешем
    @classmethod
    async def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    # Метод для генерации хеша пароля
    @classmethod
    async def get_password_hash(cls, password):
        return cls.pwd_context.hash(password)


# Класс для установки URL токена
class SetTokenUrl:
    def __init__(self, token_url: str = "token"):
        global tokenUrl  # Устанавливаем глобальный URL для токена
        tokenUrl = token_url


# Создание схемы аутентификации OAuth2, с URL для токенов
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=tokenUrl)


class GetUserFromJWT(TwoFAuth):
    # Инициализация класса
    def __init__(self, secret_key: str, algorithm: str = 'HS256'):
        """
        :param secret_key: секретный ключ для подписи JWT
        :param algorithm: алгоритм для подписи токена JWT (по умолчанию HS256)
        """
        self.secret_key = secret_key  # Секретный ключ для подписи токенов
        self.algorithm = algorithm  # Алгоритм подписи JWT

    # Метод для получения текущего пользователя по токену из куки
    async def get_user_from_cookie(self, request: Request):
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        token = request.cookies.get("access_token")  # Извлекаем токен из куки
        if token == None or token == "":
            raise HTTPException(status_code=401, detail="Token missing")
        elif token.split()[0] != "Bearer":
            raise credentials_exception  # Если схема аутентификации не "Bearer", выбрасываем исключение

        token = token.split()[-1]  # Извлекаем сам токен

        try:
            # Расшифровываем токен и извлекаем данные
            payload: dict = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            token_data = {key: val for key, val in payload.items()}  # Собираем данные токена
        except InvalidTokenError:
            raise credentials_exception  # Если токен недействителен, выбрасываем исключение

        user = UserSchemas(**token_data['user'])
        user.password = ""
        user.totp_secret = ""
        return user  # Возвращаем объект пользователя

    async def get_user_from_cookie_totp(self, request: Request, totp_key: str):
        user = await self.get_user_from_cookie(request)
        await self.verify_totp_code(user.totp_secret, totp_key)
        return user

# Класс для работы с JWT аутентификацией и хешированием паролей, наследуется от класса Hash
class JWTAuth(Hash, TwoFAuth):
    _instance = None  # Для реализации паттерна Singleton

    # Метод для создания единственного экземпляра класса (Singleton)
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(JWTAuth, cls).__new__(cls)
        return cls._instance

    # Инициализация класса
    def __init__(self, secret_key: str, database: list[object, str], algorithm: str = 'HS256',
                 token_url: str = "token"):
        """
        :param secret_key: секретный ключ для подписи JWT
        :param database: [объект базы данных, метод для получения пользователя]
        :param algorithm: алгоритм для подписи токена JWT (по умолчанию HS256)
        :param token_url: URL для токенов
        """
        SetTokenUrl(token_url=token_url)  # Установка URL для токенов
        self.secret_key = secret_key  # Секретный ключ для подписи токенов
        self.get_user = getattr(self.__check_database_include_get(database[0], database[1]),
                                database[1])  # Получение метода для поиска пользователя в базе данных
        self.algorithm = algorithm  # Алгоритм подписи JWT
        self.get_user_from_jwt = GetUserFromJWT(secret_key=secret_key, algorithm=self.algorithm)

    # Метод для аутентификации пользователя
    async def auth_user(self, filters: dict, password: str, totp_key: str = None) -> Any:
        """
        :param filters: словарь для фильтрации пользователя в базе данных, пример: {'username': 'goose'}
        :param password: пароль пользователя
        :param totp_key: код TOTP для двухфакторной аутентификации (если требуется)
        :return: объект пользователя, если аутентификация успешна, иначе выбрасывается исключение
        """
        user = await self.get_user(filters)  # Получаем пользователя по фильтрам
        if not user:
            raise UserNotFound()  # Если пользователь не найден, выбрасываем исключение

        if not await self.verify_password(password, user.password):  # Проверка пароля
            raise IncorrectPassword()  # Если пароль неверен, выбрасываем исключение

        # TODO Turn on where on totp
        # if (user.totp_secret != None and user.totp_secret != "") and totp_key == None:
        #     raise Exception("2FA activate for this is user, but totp secret is not set")
        # elif totp_key:
        #     # Если передан TOTP ключ, проверяем код двухфакторной аутентификации
        #     await self.verify_totp_code(user.totp_secret, totp_key)

        return user  # Возвращаем объект пользователя

    # Метод для создания JWT токена
    async def create_token(self, user: UserSchemas, token_data: dict = dict({}), expires_delta: int = None) -> str:
        """
        :param token_data: основные данные токена
        :param expires_delta: время жизни токена
        :return: закодированный JWT токен
        """
        to_encode = token_data.copy()  # Копируем данные токена
        to_encode['user'] = user.dict()
        if expires_delta:  # Если передано время жизни токена, добавляем его
            expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
            to_encode.update({"exp": expire})  # Добавляем метку времени "exp" для срока действия токена

        # Кодируем данные в JWT токен с использованием секретного ключа и алгоритма
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt  # Возвращаем закодированный токен

    # Метод для проверки наличия метода "get" в объекте базы данных
    @staticmethod
    def __check_database_include_get(database: object, method: str):
        if method not in dir(database):
            raise DatabaseObjectNoGetMethod()  # Если метода нет, выбрасываем исключение
        return database  # Возвращаем объект базы данных
