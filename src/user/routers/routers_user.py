from authx import TokenPayload
from fastapi import APIRouter, Depends, Header  # Импорт необходимых классов FastAPI
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter

from core.database.user import UserDB
from core.enums import StatusEnum, RoleEnum
from core.schemas.user import UserCreate, UserSchemas, UserUpdate
from core.services.auth.auth import Auth
from core.services.fernet import FernetService
from core.services.send.mail import Mail, CreateMessage, TypeEnum

# Создание маршрутизатора для организации маршрутов
router = APIRouter(
    tags=['User']
)

user_db = UserDB()
auth = Auth()
fernet = FernetService()
mail = Mail()


@router.post("/", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_user(user: UserCreate):
    user.status = StatusEnum.INACTIVE
    await user_db.create(user)
    activate_user_key = await fernet.encrypt_data(user.email)
    activate_user_key = activate_user_key.decode()
    msg = CreateMessage(
        **{
            "title": "Подтверждение почты",
            "message": f"Подтвердить почту - http://localhost:1112/api/v1/users/activate/{activate_user_key}",
            "send_to": user.email,
            "type": TypeEnum.info,
        }
    )
    await mail.send_msg(msg)
    return {"message": "User created"}


@router.get("/activate/{email_key}", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def activate_user(email_key: str):
    email = await fernet.decrypt_data(email_key.encode())
    user = await user_db.get({"email": email})
    if not user:
        return JSONResponse({"message": "User does not exist"}, 404)
    elif user.status == StatusEnum.INACTIVE:
        await user_db.update(UserUpdate(**{
            "id": user.id,
            "status": StatusEnum.ACTIVE
        }, exclude_unset=True))
        return {"message": "User activated"}
    else:
        return JSONResponse({"message": "User already activated"}, 400)


# @router.post("/", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
# async def create_user(user: UserCreate):
#     activate_user_key = await fernet.encrypt_data(json.dumps(user.dict()))
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
#     return {"message": "Send activate link to email"}
#
#
# @router.get("/activate/{activate_key}", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
# async def activate_user(activate_key: str):
#     user: UserCreate = UserCreate(**json.loads(await fernet.decrypt_data(activate_key.encode())))
#     user.status = StatusEnum.ACTIVE
#     try:
#         await user_db.create(user)
#     except Exception as e:
#         if e.args[0] == "User already exists":
#             return JSONResponse({"message": "User already exists"}, 400)
#
#         raise e
#
#     return {"message": "User approved"}


@router.delete("/")
async def delete_user(totp_code: str = Header(), pyload_token: TokenPayload = auth.auth_user()):
    user = await user_db.get({"id": int(pyload_token.sub)})
    if not auth.verify_totp(user.totp_secret, totp_code):
        return JSONResponse({"message": "Invalid TOTP"}, 403)
    await user_db.soft_delete(user.id)


@router.patch("/")
async def update_user(user_update: UserUpdate, user: TokenPayload = auth.auth_user()):
    user_role = user.get("role")
    if user_role not in (RoleEnum.ADMIN, RoleEnum.MODERATOR):
        return JSONResponse({"message": "Only Admin or Moderator can update users"}, 409)
    elif user_update.role and user_role != RoleEnum.ADMIN:
        return JSONResponse({"message": "Only Admin can update users role"}, 409)

    return await user_db.update(user_update)


@router.patch("/myself")
async def update_user_myself(user_update: UserUpdate, user: TokenPayload = auth.auth_user()):
    user_update.role = None
    user_update.status = None
    user_update.id = user.id
    return await user_db.update(user_update)


@router.get('/profile')
async def get_profile(payload: TokenPayload = auth.auth_user()) -> UserSchemas:
    user = await user_db.get({"id": int(payload.sub)})
    user.password = ""
    return user
