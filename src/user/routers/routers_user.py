import logging

from authx import TokenPayload
from fastapi import APIRouter, Depends, Header  # Импорт необходимых классов FastAPI
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter

from core.database.user import UserDB
from core.schemas.user import UserCreate, UserUpdate
from core.schemas.user import UserSchemas
from core.services.auth.auth import Auth


# Создание маршрутизатора для организации маршрутов
router = APIRouter(
    tags=['User']
)

user_db = UserDB()
auth = Auth()


@router.post("/", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_user(user: UserCreate, totp_tmp_secret: str = Header(), totp_code: str = Header()):
    res = await auth.verify_totp(totp_tmp_secret, totp_code)
    if not res:
        return JSONResponse({"message": "Invalid totp code"}, 403)

    await user_db.create(user)
    await user_db.update(UserUpdate(**{
        "totp_secret": await auth.get_uniq_totp_secret()
    }))

    return {"message": "User created"}


@router.get('/profile')
async def get_profile(payload: TokenPayload = auth.auth_user()) -> UserSchemas:
    return await user_db.get({"id": int(payload.sub)})
