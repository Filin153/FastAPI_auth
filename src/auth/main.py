import aioredis
from fastapi import FastAPI, Request, HTTPException
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from core.services.auth import Auth
from middleware import process_time_middleware, ErrorMiddleware
from routers import api_router
from core.config import settings
from core.services.send.mail import Mail

app = FastAPI()


@app.on_event("startup")
async def startup():
    redis = await aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/11", encoding="utf8", decode_responses=True)
    await FastAPILimiter.init(redis)

    Auth(app)

@app.on_event("shutdown")
async def shutdown():
    await FastAPILimiter.close()
    await Mail().close_rabbitmq()

@app.middleware('http')
async def process_time(request: Request, call_next):
    return await process_time_middleware(request, call_next)


app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_methods=['*'],
                   allow_headers=["*"],
                   allow_credentials=True, )

app.add_middleware(ErrorMiddleware)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    # Если exc.detail уже является словарём, можно вернуть его напрямую.
    # Если это не так, можно обернуть в нужный формат.
    content = exc.detail if isinstance(exc.detail, dict) else {"message": exc.detail}
    return JSONResponse(status_code=exc.status_code, content=content)

app.include_router(api_router, prefix="/api/v1")
