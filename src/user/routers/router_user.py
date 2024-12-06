from fastapi import APIRouter, HTTPException
from core.schemas.user import UserCreate
from core.database.user import UserDB
from core.services.auth.jwt_auth import Auth


# Создание маршрутизатора для организации маршрутов
router = APIRouter(
    prefix="/user",
    tags=['User']
)

user_db = UserDB()

@router.post("/")
async def create_user(user: UserCreate):
    user.password = await Auth.get_password_hash(user.password)
    try:
        return await user_db.create(user)
    except Exception as e:
        raise HTTPException(400, detail={"message": str(e)})

@router.get("/me/cookie")
async def me_cookie(user: Auth.auth_cookie):
    try:
        return user
    except Exception as e:
        raise HTTPException(400, detail={"message": str(e)})

@router.get("/me/header")
async def me_header(user: Auth.auth_cookie):
    try:
        return user
    except Exception as e:
        raise HTTPException(400, detail={"message": str(e)})