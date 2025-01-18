from fastapi import APIRouter, HTTPException, Depends
from fastapi_limiter.depends import RateLimiter

from core.database.user import UserDB
from core.schemas.user import UserCreate

# Создание маршрутизатора для организации маршрутов
router = APIRouter(
    prefix="/user",
    tags=['User']
)

user_db = UserDB()


@router.post("/", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def create_user(user: UserCreate):
    try:
        return await user_db.create(user)
    except Exception as e:
        raise HTTPException(400, detail={"message": str(e)})
