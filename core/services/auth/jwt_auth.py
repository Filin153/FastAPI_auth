from typing import Annotated, Any
from fastapi import Depends
from core.services.auth.coder import JWTAuth
from core.database.user import UserDB

class Auth(JWTAuth):
    jwt_auth = JWTAuth(secret_key="secret_key", database=[UserDB(), "get"])
    auth_cookie = Annotated[Any, Depends(jwt_auth.get_user_from_jwt.get_user_from_cookie)]

    # auth_cookie_totp = Annotated[Any, Depends(jwt_auth.get_user_from_jwt.get_user_from_cookie_totp)]