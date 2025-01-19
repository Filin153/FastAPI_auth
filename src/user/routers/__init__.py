from fastapi import APIRouter

from .routers_user import router as router_user

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(router_user)
