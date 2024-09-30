from FastAPI_auth.schemas import Token  # Импорт схемы Token, которая будет возвращаться при успешной аутентификации
from fastapi import APIRouter, Depends, HTTPException, Response  # Импорт необходимых классов FastAPI
from fastapi.security import OAuth2PasswordRequestForm  # Импорт формы для получения данных (логин и пароль) через OAuth2
from typing import Annotated, Any  # Импорт для аннотаций типов
from config import jwt_auth  # Импорт объекта jwt_auth, который отвечает за аутентификацию через JWT

# Создание маршрутизатора для организации маршрутов
router = APIRouter()

# POST-запрос для аутентификации и получения токена
@router.post("/token")
async def login(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """
    Функция для обработки запроса на аутентификацию пользователя.
    :param response: объект Response для установки куки с токеном
    :param form_data: данные из формы OAuth2PasswordRequestForm (username и password)
    :return: токен типа Token (содержит access_token и тип токена)
    """
    try:
        # Аутентификация пользователя по имени пользователя и паролю
        user = await jwt_auth.auth_user({"username": form_data.username}, form_data.password)
        if not user:
            # Если пользователь не найден или пароль неверный, возвращаем HTTP-исключение с кодом 401
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Генерация JWT токена для аутентифицированного пользователя
        access_token = await jwt_auth.create_token(
            token_data={"some_key": "some_value"},  # Дополнительные данные в токен (при необходимости)
            filter_data={'username': user.username}  # Используем имя пользователя для фильтрации
        )

        # Установка токена в куки с флагом httponly (недоступен для JavaScript) и secure (только через HTTPS)
        response.set_cookie("access_token", "Bearer " + access_token, httponly=True, secure=True)

        # Возвращаем токен в виде объекта Token
        return Token(access_token=access_token, token_type="Bearer")
    except Exception as e:
        # Если возникает ошибка, выбрасываем HTTP-исключение с кодом 401 и сообщением об ошибке
        raise HTTPException(status_code=401, detail=str(e))


# GET-запрос для получения данных текущего пользователя через заголовок Authorization
@router.get("/me/head")
async def me_head(current_user: Annotated[Any, Depends(jwt_auth.get_current_user)]):
    """
    Функция для получения текущего пользователя по токену из заголовка Authorization.
    :param current_user: объект текущего пользователя, извлеченный из JWT токена
    :return: информация о текущем пользователе
    """
    return current_user  # Возвращаем объект пользователя (в зависимости от реализации это может быть JSON с данными)

# GET-запрос для получения данных текущего пользователя через куки
@router.get("/me/cookie")
async def me_cookie(current_user: Annotated[Any, Depends(jwt_auth.get_current_user_cookie)]):
    """
    Функция для получения текущего пользователя по токену, сохраненному в куки.
    :param current_user: объект текущего пользователя, извлеченный из JWT токена, который хранится в куки
    :return: информация о текущем пользователе
    """
    return current_user  # Возвращаем объект пользователя (данные о пользователе)
