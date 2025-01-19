from http.client import HTTPException

from authx import TokenPayload
from fastapi import APIRouter, Depends, Response  # Импорт необходимых классов FastAPI
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter

from core.database.user import UserDB
from core.schemas.user import UserAuthData
from core.services.auth.auth import Auth
from core.services.password import Hash

# Создание маршрутизатора для организации маршрутов
router = APIRouter(
    tags=['Auth']
)

user_db = UserDB()
auth = Auth()


@router.post('/token', dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def token(data: UserAuthData, response: Response):
    if data.username:
        user = await user_db.get({"username": data.username})
    elif data.email:
        user = await user_db.get({"email": data.email})
    else:
        return JSONResponse({"message": "Missing username/email"}, 422)

    if user is None:
        raise HTTPException(401, "User does not exist")
    elif Hash.verify_password(data.password, user.password):
        access_token, refresh_token = await auth.create_token(uid=str(user.id), response=response, role=user.role)
        return {"message": "Token create successfully", "access_token": access_token, "refresh_token": refresh_token}

    return JSONResponse({"message": "Bad username/password"}, 401)


@router.get('/login', dependencies=[Depends(RateLimiter(times=10, seconds=60)), auth.auth_user()])
async def login():
    return {"message": "Login in successfully"}


@router.post('/refresh', dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def refresh(access_token: TokenPayload = auth.refresh_token()):
    return {"message": "Refresh in successfully", "access_token": access_token}


@router.post('/logout', dependencies=[Depends(RateLimiter(times=10, seconds=60)), auth.logout()])
async def logout():
    return {"message": "Logout in successfully"}
