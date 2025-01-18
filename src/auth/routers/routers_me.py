from authx import TokenPayload
from fastapi import APIRouter, Depends  # Импорт необходимых классов FastAPI

from core.services.auth.auth import Auth
from core.database.user import UserDB
from core.schemas.user import UserSchemas

# Создание маршрутизатора для организации маршрутов
router = APIRouter(
    tags=['User Info']
)

user_db = UserDB()
auth = Auth.auth


@router.get('/profile')
async def get_profile(payload: TokenPayload = Depends(auth.access_token_required)) -> UserSchemas:
    return await user_db.get({"id": int(payload.sub)})
