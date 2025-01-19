from fastapi import APIRouter, HTTPException, Depends
from fastapi_limiter.depends import RateLimiter
from fastapi.responses import JSONResponse
from core.database.user import UserDB
from core.schemas.user import UserCreate

# Создание маршрутизатора для организации маршрутов
router = APIRouter(
    tags=['User']
)

user_db = UserDB()


@router.post("/", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_user(user: UserCreate):
    try:
        return await user_db.create(user)
    except Exception as e:
        return JSONResponse({"message": str(e)}, 400)
