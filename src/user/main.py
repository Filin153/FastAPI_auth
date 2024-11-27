from fastapi import FastAPI
from routers.router_user import router as user_r

app = FastAPI()

app.include_router(user_r)
