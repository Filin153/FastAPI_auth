from typing import Annotated, Any
from fastapi import Depends
from .coder import JWTAuth
from .database.user import UserDB

class Auth(JWTAuth):
    jwt_auth = JWTAuth(secret_key="secret_key", database=[UserDB(), "get"])
    auth_cookie = Annotated[Any, Depends(jwt_auth.get_current_user_cookie)]

    auth_cookie_totp = Annotated[Any, Depends(jwt_auth.get_current_user_cookie_totp)]