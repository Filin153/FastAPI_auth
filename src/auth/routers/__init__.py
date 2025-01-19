from fastapi import APIRouter

from .routers_auth import router as router_auth
from .routers_totp import router as router_totp

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(router_auth)
api_router.include_router(router_totp)
