from typing import Annotated, Any
from fastapi import Depends
from FastAPI_auth.coder import JWTAuth
from config import FakeDB

class Auth(JWTAuth):
    jwt_auth = JWTAuth(secret_key="qweqweasdasd", database=[FakeDB(), "get"])
    auth_cookie = Annotated[Any, Depends(jwt_auth.get_current_user_cookie)]
    auth_header = Annotated[Any, Depends(jwt_auth.get_current_user_header)]