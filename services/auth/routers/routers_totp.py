import io

from authx import TokenPayload
from fastapi import APIRouter, Depends, HTTPException  # Импорт необходимых классов FastAPI
from fastapi_limiter.depends import RateLimiter
from starlette.responses import StreamingResponse, JSONResponse

from common.interfaces.user import UserInterface
from common.schemas.user import UserCreate, UserUpdate, UserFilters
from common.services.auth.auth import Auth

# Создание маршрутизатора для организации маршрутов
router = APIRouter(
    tags=['TOTP']
)

user_interface = UserInterface()
auth = Auth()


@router.post("/totp/activate", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def totp_activate(payload: TokenPayload = auth.auth_user()):
    await user_interface.update_in_database(UserUpdate(**{
        "totp_secret": await auth.get_uniq_totp_secret()
    }), sub=int(payload.sub))
    return {"message": "TOTP activated"}


@router.post('/totp', dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def totp(payload: TokenPayload = auth.auth_user(), user_create: UserCreate = None):
    if user_create:
        user = await user_interface.get_from_database(UserFilters(**{"email": user_create.email}))
        await auth.verify_password(user_create.password, user.password)
    else:
        user = await user_interface.get_from_database(UserFilters(**{"id": int(payload.sub)}))

    if user.totp_secret is None or user.totp_secret == "":
        return JSONResponse({"message": "TOTP is not activate for user"}, status_code=400)

    return await auth.send_totp_code(user)


@router.post('/totp/qr', dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def totp_qr(payload: TokenPayload = auth.auth_user(), user_create: UserCreate = None):
    if user_create:
        user = await user_interface.get_from_database(UserFilters(**{"email": user_create.email}))
        await auth.verify_password(user_create.password, user.password)
    else:
        user = await user_interface.get_from_database(UserFilters(**{"id": int(payload.sub)}))

    if user.totp_secret is None or user.totp_secret == "":
        return JSONResponse({"message": "TOTP is not activate for user"}, status_code=400)

    try:
        qr_bytes = await auth.get_totp_qr_code(user.totp_secret, user.email)
        return StreamingResponse(io.BytesIO(qr_bytes), media_type="image/svg+xml")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
