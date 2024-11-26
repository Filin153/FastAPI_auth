from fastapi import APIRouter, HTTPException
from .schemas import UserSchemas
from .database.user import UserDB
from FastAPI_auth.jwt_auth import Auth


# Создание маршрутизатора для организации маршрутов
router = APIRouter(
    prefix="/user",
    tags=['User']
)

user_db = UserDB()

@router.post("")
async def create_user(user: UserSchemas):
    user.password = await Auth.get_password_hash(user.password)
    try:
        return await user_db.create(user)
    except Exception as e:
        raise HTTPException(400, detail={"message": str(e)})