from fastapi import APIRouter

from .routers_auth import router as router_auth
from .routers_me import router as router_me

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(router_me)
api_router.include_router(router_auth)
