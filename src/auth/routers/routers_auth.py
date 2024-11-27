from fastapi import APIRouter, Response  # Импорт необходимых классов FastAPI
from fastapi.security import OAuth2PasswordRequestForm  # Импорт формы для получения данных (логин и пароль) через OAuth2
from core.services.auth.jwt_auth import Auth
from fastapi import HTTPException, Depends
from typing import Annotated

# Создание маршрутизатора для организации маршрутов
router = APIRouter(
    tags=['Auth']
)

# POST-запрос для аутентификации и получения токена
@router.post("/token")
async def token(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    """
    Функция для обработки запроса на аутентификацию пользователя.
    :param response: объект Response для установки куки с токеном
    :param form_data: данные из формы OAuth2PasswordRequestForm (username и password)
    :return: токен типа Token (содержит access_token и тип токена)
    """
    try:
        # Аутентификация пользователя по имени пользователя и паролю
        user = await Auth.jwt_auth.auth_user({"username": form_data.username}, form_data.password)
        if not user:
            # Если пользователь не найден или пароль неверный, возвращаем HTTP-исключение с кодом 401
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Генерация JWT токена для аутентифицированного пользователя
        access_token = await Auth.jwt_auth.create_token(
            user=user,
            token_data={"client_id": form_data.client_id, "client_secret": form_data.client_secret},  # Дополнительные данные в токен (при необходимости)
        )

        # Установка токена в куки с флагом httponly (недоступен для JavaScript) и secure (только через HTTPS)
        response.set_cookie("access_token", "Bearer " + access_token, httponly=True, secure=True)

        # Возвращаем токен в виде объекта Token
        return {"message": "successful create access token"}
    except Exception as e:
        # Если возникает ошибка, выбрасываем HTTP-исключение с кодом 401 и сообщением об ошибке
        raise HTTPException(status_code=401, detail=str(e))


# @router.post("/totp")
# async def token_totp(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> StreamingResponse:
#     try:
#         # Аутентификация пользователя по имени пользователя и паролю
#         # Мы вызываем метод 'auth_user', который проверяет существование пользователя и правильность пароля
#         # Если имя пользователя и пароль не совпадают с хранящимися данными, метод возвращает None
#         user = await Auth.jwt_auth.auth_user({"username": form_data.username}, form_data.password)
#
#         if not user:
#             # Если пользователь не найден или пароль неверный, вызываем HTTP-исключение с кодом 401 (Unauthorized)
#             # Сообщение в 'detail' указывает, что имя пользователя или пароль некорректны
#             raise HTTPException(
#                 status_code=401,
#                 detail="Incorrect username or password",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#
#         # Генерация нового TOTP секретного ключа для пользователя
#         # Этот ключ используется для последующей генерации одноразовых паролей
#         totp_token = await Auth.jwt_auth.get_new_totp_secret_key()
#
#         # В реальном приложении этот сгенерированный ключ totp_token необходимо сохранить в базе данных
#         # для пользователя, чтобы он мог использовать его для двухфакторной аутентификации.
#         # Предполагается, что здесь будет запрос в БД на сохранение totp_token.
#
#         # Использование pyotp для создания URL для конфигурации двухфакторной аутентификации
#         # 'provisioning_uri' создаёт специальный URL для добавления в приложения вроде Google Authenticator
#         # Пользователь сканирует этот QR-код или вводит данные вручную в своё приложение 2FA
#         # Получение TOTP URL
#         totp_url = await Auth.jwt_auth.get_totp_url(totp_token, user.username)
#
#         # Генерация QR-кода
#         qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
#         qr.add_data(totp_url)
#         qr.make(fit=True)
#
#         # Создание изображения QR-кода
#         img = qr.make_image(fill='black', back_color='white')
#
#         # Сохранение изображения в байтовый поток
#         img_io = BytesIO()
#         img.save(img_io, 'PNG')
#         img_io.seek(0)
#
#         # Возвращаем изображение в виде ответа
#         return StreamingResponse(img_io, media_type="image/png")
#     except Exception as e:
#         # Обработка исключений. Если возникает ошибка, возвращается исключение HTTP с кодом 401 (Unauthorized)
#         # и описание ошибки передаётся в качестве 'detail'
#         raise HTTPException(status_code=401, detail=str(e))


# GET-запрос для получения данных текущего пользователя через куки
@router.get("/login")
async def login_cookie(current_user: Auth.auth_cookie):
    """
    Функция для получения текущего пользователя по токену, сохраненному в куки.
    :param current_user: объект текущего пользователя, извлеченный из JWT токена, который хранится в куки
    :return: информация о текущем пользователе
    """
    return {"message": "successful login"}  # Возвращаем объект пользователя (данные о пользователе)

@router.post("/logout")
async def logout_cookie(response: Response):
    response.set_cookie("access_token", "", httponly=True, secure=True)
    return {"message": "successful logout"}