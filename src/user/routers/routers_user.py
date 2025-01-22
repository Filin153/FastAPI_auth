from authx import TokenPayload
from fastapi import APIRouter, Depends  # Импорт необходимых классов FastAPI
from fastapi_limiter.depends import RateLimiter

from core.database.user import UserDB
from core.enums import StatusEnum
from core.schemas.user import UserCreate, UserUpdate
from core.schemas.user import UserSchemas
from core.services.auth.auth import Auth
from core.services.send.rabbitmq import add_new_msg_task
from core.services.send.schemas import CreateMessage, TypeEnum
from core.services.fernet import FernetService

# Создание маршрутизатора для организации маршрутов
router = APIRouter(
    tags=['User']
)

user_db = UserDB()
auth = Auth()
fernet = FernetService()

@router.post("/", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_user(user: UserCreate):
    user.satus = StatusEnum.INACTIVE
    await user_db.create(user)
    msg = CreateMessage(
        **{
            "title": "Подтверждение почты",
            "message": f"Подтвердить почту - http://localhost:1112/api/v1/users/activate/{str(await fernet.encrypt_data(user.email))}",
            "send_to": user.email,
            "type": TypeEnum.info,
        }
    )
    await add_new_msg_task(msg)
    return {"message": "User created"}

@router.get("/activate/{email_key}", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def activate_user(email_key: str):
    email = await fernet.decrypt_data(email_key)
    user = await user_db.get({"email": email})
    if not user:
        return {"message": "User does not exist"}
    elif user.status == StatusEnum.INACTIVE:
        await user_db.update(UserUpdate(**{
            "status": StatusEnum.ACTIVE
        }))
        return {"message": "User activated"}
    else:
        return {"message": "User already activated"}

# TODO Delete user
# TODO First admin user
# TODO Edit user status
# TODO Edit user role

# @router.post("/", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
# async def create_user(user: UserCreate, totp_tmp_secret: str = Header(), totp_code: str = Header()):
#     res = await auth.verify_totp(totp_tmp_secret, totp_code)
#     if not res:
#         return JSONResponse({"message": "Invalid totp code"}, 403)
#
#     await user_db.create(user)
#     await user_db.update(UserUpdate(**{
#         "totp_secret": await auth.get_uniq_totp_secret()
#     }))
#
#     return {"message": "User created"}


@router.get('/profile')
async def get_profile(payload: TokenPayload = auth.auth_user()) -> UserSchemas:
    return await user_db.get({"id": int(payload.sub)})
