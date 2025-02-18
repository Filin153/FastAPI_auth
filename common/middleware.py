from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time

async def process_time_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start
    response.headers["X-Process-Time"] = str(process_time)
    return response

class ErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

async def custom_http_exception_handler(request: Request, exc: HTTPException):
    # Если exc.detail уже является словарём, можно вернуть его напрямую.
    # Если это не так, можно обернуть в нужный формат.
    content = exc.detail if isinstance(exc.detail, dict) else {"message": exc.detail}
    return JSONResponse(status_code=exc.status_code, content=content)