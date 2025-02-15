from authx import TokenPayload
from fastapi import APIRouter, Depends, Response  # Импорт необходимых классов FastAPI
from fastapi_limiter.depends import RateLimiter

from common.interfaces.user import UserInterface
from common.schemas.user import UserAuthData, UserFilters
from common.services.auth.auth import Auth

# Создание маршрутизатора для организации маршрутов
router = APIRouter(
    tags=['Auth']
)

user_interface = UserInterface()
auth = Auth()


@router.post('/token', dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def token(user_auth_data: UserAuthData, response: Response):
    user = await user_interface.get_from_database(UserFilters(**{"email": user_auth_data.email}), with_password=True)
    return await auth.verify_user_and_create_token(user=user, user_auth_data=user_auth_data, response=response)


@router.get('/login', dependencies=[Depends(RateLimiter(times=10, seconds=60)), auth.auth_user()])
async def login():
    return {"message": "Login in successfully"}


@router.post('/refresh', dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def refresh(access_token: TokenPayload = auth.refresh_token()):
    return {"message": "Refresh in successfully", "access_token": access_token}


@router.post('/logout', dependencies=[Depends(RateLimiter(times=10, seconds=60)), auth.logout()])
async def logout():
    return {"message": "Logout in successfully"}
