from fastapi import FastAPI
from FastAPI_auth.routers_auth import router as auth_router
from FastAPI_auth.router_user import router as user_router
from FastAPI_auth.models import Base
from FastAPI_auth.database.database import engine, get_session
from FastAPI_auth.models import UserModel
from passlib.context import CryptContext


app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with get_session() as session:
        user = UserModel()
        user.username = "testuser"
        user.password = CryptContext(schemes=['bcrypt']).hash('testpassword')
        user.totp_secret = None
        session.add(user)
        await session.commit()
        await session.refresh(user)


app.include_router(auth_router)
app.include_router(user_router)