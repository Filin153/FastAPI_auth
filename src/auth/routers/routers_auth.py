from http.client import HTTPException

from authx import TokenPayload
from fastapi import APIRouter, Depends  # Импорт необходимых классов FastAPI
from fastapi.openapi.models import Response
from fastapi_limiter.depends import RateLimiter

from core.schemas.user import UserAuthData
from core.services.auth.auth import Auth
from core.database.user import UserDB
from core.services.password import Hash

# Создание маршрутизатора для организации маршрутов
router = APIRouter(
    tags=['Auth']
)

user_db = UserDB()
auth = Auth().auth


@router.post('/token', dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def token(data: UserAuthData, response: Response):
    if data.username:
        user = await user_db.get({"username": data.username})
    elif data.email:
        user = await user_db.get({"email": data.email})
    else:
        raise HTTPException(422, "Missing username/email")

    if user is None:
        raise HTTPException(401, "User does not exist")
    elif Hash.verify_password(data.password, user.password):
        access_token = auth.create_access_token(uid=user.id, role=user.role)
        refresh_token = auth.create_refresh_token(user.id)
        auth.set_access_cookies(access_token, response=response)
        auth.set_refresh_cookies(refresh_token, response=response)

        return {"message": "Logged in successfully"}

    raise HTTPException(401, "Bad username/password")

@router.post('/login', dependencies=[Depends(RateLimiter(times=5, seconds=60)), Depends(auth.access_token_required)])
async def login():
    return {"message": "Logged in successfully"}


@router.post('/refresh')
async def refresh(
        response: Response,
        refresh_payload: TokenPayload = Depends(auth.refresh_token_required),
):
    access_token = auth.create_access_token(refresh_payload.sub)
    auth.set_access_cookies(access_token, response=response)
    return {"message": "Refresh in successfully"}
