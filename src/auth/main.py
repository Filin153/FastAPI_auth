from fastapi import FastAPI
from routers.routers_auth import router as auth_r

app = FastAPI()

app.include_router(auth_r)

