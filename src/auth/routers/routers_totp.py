import logging
from http.client import HTTPException

from authx import TokenPayload
from fastapi import APIRouter, Depends, Response  # Импорт необходимых классов FastAPI
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter
from fastapi import Request
from pydantic import EmailStr

from core.database.user import UserDB
from core.schemas.user import UserAuthData, UserCreate
from core.services.auth.auth import Auth
from core.services.password import Hash

# Создание маршрутизатора для организации маршрутов
router = APIRouter(
    tags=['TOTP']
)

user_db = UserDB()
auth = Auth()


# TODO Auth user on Password and Email, and then send msg
@router.post('/totp', dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def totp(request: Request, email: EmailStr | None = None):
    if email:
        return await auth.send_totp_code(email)
    else:
        token_payload: TokenPayload = await auth.auth_user()(request)
        user = await user_db.get({"id": int(token_payload.sub)})
        return await auth.send_totp_code(user)

