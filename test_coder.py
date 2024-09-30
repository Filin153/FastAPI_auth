import pytest
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException
from FastAPI_auth.coder import JWTAuth, Hash, UserNotFound, IncorrectPassword, DatabaseObjectNoGetMethod


# Фиктивная база данных и пользователь
class FakeDB:
    def __init__(self):
        self.users = {
            'testuser': {'password': CryptContext(schemes=['bcrypt']).hash('testpassword')}
        }

    def get_user(self, filters: dict):
        username = filters.get('username')
        if username in self.users:
            user = type('User', (), {})()  # Создаем объект User динамически
            user.username = username
            user.password = self.users[username]['password']
            return user
        return None


# Создание JWTAuth объекта с фиктивной базой данных
@pytest.fixture
def jwt_auth():
    return JWTAuth(secret_key="testsecret", database=[FakeDB(), 'get_user'])


# Тестирование асинхронного хеширования пароля
@pytest.mark.asyncio
async def test_password_hashing():
    password = "testpassword"
    hashed_password = await Hash.get_password_hash(password)
    assert await Hash.verify_password(password, hashed_password)


# Тестирование правильной асинхронной аутентификации пользователя
@pytest.mark.asyncio
async def test_auth_user_success(jwt_auth):
    user = await jwt_auth.auth_user({'username': 'testuser'}, 'testpassword')
    assert user.username == 'testuser'


# Тестирование некорректной асинхронной аутентификации пользователя
@pytest.mark.asyncio
async def test_auth_user_incorrect_password(jwt_auth):
    with pytest.raises(IncorrectPassword):
        await jwt_auth.auth_user({'username': 'testuser'}, 'wrongpassword')


@pytest.mark.asyncio
async def test_auth_user_not_found(jwt_auth):
    with pytest.raises(UserNotFound):
        await jwt_auth.auth_user({'username': 'unknownuser'}, 'testpassword')


# Тестирование асинхронного создания токена
@pytest.mark.asyncio
async def test_create_token(jwt_auth):
    token_data = {'sub': 'testuser'}
    filters = {'username': 'testuser'}
    token = await jwt_auth.create_token(token_data=token_data, filter_data=filters, expires_delta=30)
    decoded_token = jwt.decode(token, jwt_auth.secret_key, algorithms=[jwt_auth.algorithm])

    assert decoded_token['sub'] == 'testuser'
    assert 'exp' in decoded_token
    assert decoded_token['filters'] == filters


# Тестирование асинхронного получения текущего пользователя по токену
@pytest.mark.asyncio
async def test_get_current_user(jwt_auth):
    token_data = {'sub': 'testuser'}
    filters = {'username': 'testuser'}
    token = await jwt_auth.create_token(token_data=token_data, filter_data=filters, expires_delta=30)

    user = await jwt_auth.get_current_user(token)
    assert user.username == 'testuser'


# Тестирование неправильного токена
@pytest.mark.asyncio
async def test_get_current_user_invalid_token(jwt_auth):
    invalid_token = "invalidtoken"
    with pytest.raises(HTTPException):
        await jwt_auth.get_current_user(invalid_token)


# Тестирование ошибки, если в базе данных нет метода get
def test_database_no_get_method():
    class InvalidDB:
        pass

    with pytest.raises(DatabaseObjectNoGetMethod):
        JWTAuth(secret_key="testsecret", database=[InvalidDB(), 'get_user'])
