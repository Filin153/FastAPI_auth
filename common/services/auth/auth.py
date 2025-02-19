from datetime import timedelta
from threading import Lock
from fastapi import HTTPException
from authx import AuthXConfig, AuthX, RequestToken, \
    TokenPayload  # Предполагается, что этот класс определён в пакете authx
from fastapi import FastAPI, Depends, Response, Request
from fastapi.responses import JSONResponse

from common.config import settings
from common.enums import StatusEnum
from common.schemas.user import UserAuthData, UserSchemas
from common.services.auth.totp import TOTPService
from common.services.password import Hash


class Auth(TOTPService, Hash):
    AUTH_CONFIG = AuthXConfig(
        JWT_SECRET_KEY=settings.JWT_SECRET_KEY,

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
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=30),

        # Локации, где передаётся токен (в данном случае: заголовки и cookies)
        JWT_TOKEN_LOCATION=["headers", "cookies"],

        # Опции для HTTP заголовков
        JWT_HEADER_NAME="Authorization",
        JWT_HEADER_TYPE="Bearer",

        # Опции для cookies (access token)
        JWT_ACCESS_COOKIE_NAME="access_token",
        JWT_ACCESS_COOKIE_PATH="/",
        JWT_COOKIE_CSRF_PROTECT=True,
        JWT_COOKIE_DOMAIN=None,
        JWT_COOKIE_MAX_AGE=None,
        JWT_COOKIE_SAMESITE="lax",
        JWT_COOKIE_SECURE=True,

        # Опции для cookies (refresh token)
        JWT_REFRESH_COOKIE_NAME="refresh_token",
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
    _lock = Lock()  # Для потокобезопасной инициализации

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def __init__(cls, app: FastAPI | None = None) -> None:
        super().__init__(cls)
        if not cls.__true:
            cls.auth: AuthX = AuthX(config=cls.AUTH_CONFIG)
            if app:
                cls.auth.handle_errors(app)

                cls.__true = True

    async def __set_csrf_to_token(self, request: Request, token: RequestToken) -> RequestToken:
        csrf_header_name = (
            self.auth.config.JWT_ACCESS_CSRF_HEADER_NAME
            if token.type == "access"
            else self.auth.config.JWT_REFRESH_CSRF_HEADER_NAME
        )
        csrf_cookie_name = (
            self.auth.config.JWT_ACCESS_CSRF_COOKIE_NAME
            if token.type == "access"
            else self.auth.config.JWT_REFRESH_CSRF_COOKIE_NAME
        )

        csrf_token_header = request.headers.get(csrf_header_name)
        csrf_token_cookie = request.cookies.get(csrf_cookie_name)

        if not csrf_token_header:
            raise ValueError(f"Missing CSRF token in header: {csrf_header_name}")
        elif not csrf_token_cookie:
            raise ValueError(f"Missing CSRF token in cookies: {csrf_cookie_name}")

        csrf_token_header = csrf_token_header.strip()
        csrf_token_cookie = csrf_token_cookie.strip()

        if csrf_token_header != csrf_token_cookie:
            raise ValueError("CSRF tokens from header and cookies do not match.")

        token.csrf = csrf_token_header
        return token

    def logout(self):
        async def wrapper(response: Response):
            self.auth.unset_access_cookies(response)
            self.auth.unset_refresh_cookies(response)

        return Depends(wrapper)

    def refresh_token(self):
        async def wrapper(request: Request, response: Response,
                          token: RequestToken = Depends(self.auth.get_token_from_request(type="refresh"))):
            if "X-CSRF-TOKEN" not in request.headers:
                raise HTTPException(400, {"message": "Missing X-CSRF-TOKEN"})

            if token.location == "cookies":
                token = await self.__set_csrf_to_token(request, token)
                token_payload = self.auth.verify_token(token=token)
            else:
                token_payload = self.auth.verify_token(token=token, verify_csrf=False)

            access_token = self.auth.create_access_token(token_payload.sub)
            self.auth.set_access_cookies(access_token, response=response)
            return access_token  # payload можно вернуть для дальнейшего использования в эндпоинте

        return Depends(wrapper)

    def auth_user(self, allowed_roles: list[str] = ["*"]):
        async def wrapper(request: Request) -> TokenPayload | JSONResponse:
            token: RequestToken = await self.auth._get_token_from_request(
                request,
                None,  # Explicitly passing None for locations
                refresh=False,
                optional=True,
            )

            if not token:
                raise HTTPException(400, {"message": self.auth.MSG_MissingTokenError})

            if token.location == "cookies":
                if "X-CSRF-TOKEN" not in request.headers:
                    raise HTTPException(400, {"message": "Missing X-CSRF-TOKEN"})
                elif self.auth.config.JWT_ACCESS_CSRF_COOKIE_NAME not in request.cookies:
                    raise HTTPException(400, {"message": "Missing csrf_access_token"})

                token = await self.__set_csrf_to_token(request, token)
                token_payload = self.auth.verify_token(token=token)
            else:
                token_payload = self.auth.verify_token(token=token, verify_csrf=False)

            if len(allowed_roles) == 1 and "*" == allowed_roles[0]:
                return token_payload

            # Извлекаем роль пользователя
            user_role = token_payload.get("role")
            if user_role not in allowed_roles:
                raise HTTPException(403, {"message": "Permissions denied"})
            return token_payload  # payload можно вернуть для дальнейшего использования в эндпоинте

        return Depends(wrapper)

    async def verify_user_and_create_token(self, user: UserSchemas, user_auth_data: UserAuthData, response: Response, totp: bool = True):
        if user is None:
            return JSONResponse({"message": "User does not exist"}, 404)
        elif user.status in (StatusEnum.INACTIVE, StatusEnum.BANNED):
            return JSONResponse({"message": "User banned or inactive"}, 409)
        elif not await self.verify_password(user_auth_data.password, user.password):
            return JSONResponse({"message": "Invalid password"}, 403)
        elif user.totp_secret and totp:
            if user_auth_data.totp_code is None:
                return JSONResponse({"message": "Missing totp code"}, 403)
            totp_res = await self.verify_totp(user.totp_secret, user_auth_data.totp_code)
            if not totp_res:
                return JSONResponse({"message": "Invalid totp code"}, 403)

        access_token = self.auth.create_access_token(uid=str(user.id), role=user.role)
        refresh_token = self.auth.create_refresh_token(uid=str(user.id))
        self.auth.set_access_cookies(access_token, response=response)
        self.auth.set_refresh_cookies(refresh_token, response=response)

        return {"message": "Token create successfully", "access_token": access_token,
                "refresh_token": refresh_token}
