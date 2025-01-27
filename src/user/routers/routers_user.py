import json

from authx import TokenPayload
from fastapi import APIRouter, Depends, Header  # Импорт необходимых классов FastAPI
from fastapi_limiter.depends import RateLimiter
from fastapi.responses import JSONResponse

from core.database.user import UserDB
from core.enums import StatusEnum
from core.schemas.user import UserCreate, UserUpdate, UserSchemas
from core.services.auth.auth import Auth
from core.services.fernet import FernetService
from core.services.send.rabbitmq import add_new_msg_task
from core.services.send.schemas import CreateMessage, TypeEnum

# Создание маршрутизатора для организации маршрутов
router = APIRouter(
    tags=['User']
)

user_db = UserDB()
auth = Auth()
fernet = FernetService()


# @router.post("/", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
# async def create_user(user: UserCreate):
#     user.status = StatusEnum.INACTIVE
#     await user_db.create(user)
#     activate_user_key = await fernet.encrypt_data(user.email)
#     activate_user_key = activate_user_key.decode()
#     msg = CreateMessage(
#         **{
#             "title": "Подтверждение почты",
#             "message": f"Подтвердить почту - http://localhost:1112/api/v1/users/activate/{activate_user_key}",
#             "send_to": user.email,
#             "type": TypeEnum.info,
#         }
#     )
#     await add_new_msg_task(msg)
#     return {"message": "User created"}
#
#
# @router.get("/activate/{email_key}", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
# async def activate_user(email_key: str):
#     email = await fernet.decrypt_data(email_key.encode())
#     user = await user_db.get({"email": email})
#     if not user:
#         return {"message": "User does not exist"}
#     elif user.status == StatusEnum.INACTIVE:
#         await user_db.update(UserUpdate(**{
#             "id": user.id,
#             "status": StatusEnum.ACTIVE
#         }, exclude_unset=True))
#         return {"message": "User activated"}
#     else:
#         return {"message": "User already activated"}

@router.post("/", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_user(user: UserCreate):
    activate_user_key = await fernet.encrypt_data(json.dumps(user.dict()))
    activate_user_key = activate_user_key.decode()
    msg = CreateMessage(
        **{
            "title": "Подтверждение почты",
            "message": f"Подтвердить почту - http://localhost:1112/api/v1/users/activate/{activate_user_key}",
            "send_to": user.email,
            "type": TypeEnum.info,
        }
    )
    await add_new_msg_task(msg)
    return {"message": "Send activate link to email"}


@router.get("/activate/{activate_key}", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def activate_user(activate_key: str):
    user: UserCreate = UserCreate(**json.loads(await fernet.decrypt_data(activate_key.encode())))
    user.status = StatusEnum.ACTIVE
    await user_db.create(user)
    return {"message": "User created"}



@router.delete("/")
async def delete_user(totp_code: str = Header(), pyload_token: TokenPayload = auth.auth_user()):
    user = await user_db.get({"id": int(pyload_token.sub)})
    if not auth.verify_totp(user.totp_secret, totp_code):
        return JSONResponse({"message": "Invalid TOTP"}, 403)
    await user_db.soft_delete(user.id)



# TODO Edit user status
# TODO Edit user role


@router.get('/profile')
async def get_profile(payload: TokenPayload = auth.auth_user()) -> UserSchemas:
    return await user_db.get({"id": int(payload.sub)})
