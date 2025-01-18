import os
from datetime import timedelta
from http.client import HTTPException
from threading import Lock

from authx import AuthXConfig, AuthX, RequestToken  # Предполагается, что этот класс определён в пакете authx
from dotenv import load_dotenv
from fastapi import FastAPI, Depends

load_dotenv()

load_dotenv()


class Auth:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    AUTH_CONFIG = AuthXConfig(
        JWT_SECRET_KEY=JWT_SECRET_KEY,

        # Access и Refresh Token таймауты и криптографические настройки
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=15),
        JWT_ALGORITHM="HS256",
        JWT_DECODE_ALGORITHMS=["HS256"],
        JWT_DECODE_AUDIENCE=None,
        JWT_DECODE_ISSUER=None,
        JWT_DECODE_LEEWAY=0,
        JWT_ENCODE_AUDIENCE=None,
        JWT_ENCODE_ISSUER=None,
        JWT_ENCODE_NBF=True,
        JWT_ERROR_MESSAGE_KEY="message",
        JWT_IDENTITY_CLAIM="sub",
        JWT_PRIVATE_KEY=None,
        JWT_PUBLIC_KEY=None,
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=20),

        # Локации, где передаётся токен (в данном случае: заголовки и cookies)
        JWT_TOKEN_LOCATION=["headers", "cookies"],

        # Опции для HTTP заголовков
        JWT_HEADER_NAME="Authorization",
        JWT_HEADER_TYPE="Bearer",

        # Опции для cookies (access token)
        JWT_ACCESS_COOKIE_NAME="access_token_cookie",
        JWT_ACCESS_COOKIE_PATH="/",
        JWT_COOKIE_CSRF_PROTECT=True,
        JWT_COOKIE_DOMAIN=None,
        JWT_COOKIE_MAX_AGE=None,
        JWT_COOKIE_SAMESITE="lax",
        JWT_COOKIE_SECURE=True,

        # Опции для cookies (refresh token)
        JWT_REFRESH_COOKIE_NAME="refresh_token_cookie",
        JWT_REFRESH_COOKIE_PATH="/",
        JWT_SESSION_COOKIE=True,

        # CSRF защита (access token)
        JWT_ACCESS_CSRF_COOKIE_NAME="csrf_access_token",
        JWT_ACCESS_CSRF_COOKIE_PATH="/",
        JWT_ACCESS_CSRF_FIELD_NAME="csrf_token",
        JWT_ACCESS_CSRF_HEADER_NAME="X-CSRF-TOKEN",

        # CSRF защита (refresh token)
        JWT_REFRESH_CSRF_COOKIE_NAME="csrf_refresh_token",  # Если необходимо, можно задать "csrf_refresh_cookie"
        JWT_REFRESH_CSRF_COOKIE_PATH="/",
        JWT_REFRESH_CSRF_FIELD_NAME="csrf_token",
        JWT_REFRESH_CSRF_HEADER_NAME="X-CSRF-TOKEN",

        # Опции для CSRF проверки
        JWT_CSRF_CHECK_FORM=False,
        JWT_CSRF_IN_COOKIES=True,
        JWT_CSRF_METHODS=["POST", "PUT", "PATCH", "DELETE"],

        # Опции для передачи токена через query параметры или JSON
        JWT_QUERY_STRING_NAME="token",
        JWT_JSON_KEY="access_token",
        JWT_REFRESH_JSON_KEY="refresh_token",

        # Опции для имплицитного обновления (implicit refresh)
        JWT_IMPLICIT_REFRESH_ROUTE_EXCLUDE=[],
        JWT_IMPLICIT_REFRESH_ROUTE_INCLUDE=[],
        JWT_IMPLICIT_REFRESH_METHOD_EXCLUDE=[],
        JWT_IMPLICIT_REFRESH_METHOD_INCLUDE=[],
        JWT_IMPLICIT_REFRESH_DELTATIME=timedelta(minutes=10)
    )

    auth: AuthX = None
    __true = False
    _instance = None  # Для хранения единственного экземпляра
    _lock = Lock()    # Для потокобезопасной инициализации

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def __init__(cls, app: FastAPI | None = None) -> None:
        if not cls.__true:
            cls.auth: AuthX = AuthX(config=cls.AUTH_CONFIG)
            if app:
                cls.auth.handle_errors(app)
                cls.__true = True

    def role_checker(self, allowed_roles: list[str]):
        async def wrapper(token: RequestToken = Depends(self.auth.get_token_from_request)):
            token_payload = self.auth.verify_token(token=token)

            if len(allowed_roles) == 1 and "*" == allowed_roles[0]:
                return token_payload

            # Извлекаем роль пользователя
            user_role = token_payload.get("role")
            if user_role not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail={"message": "Permissions denied"}
                )
            return token_payload  # payload можно вернуть для дальнейшего использования в эндпоинте

        return Depends(wrapper)
