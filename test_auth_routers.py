import pytest
from fastapi.testclient import TestClient
from FastAPI_auth.routers import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

client = TestClient(app)

# Тестовые данные для входа
test_username = "testuser"
test_password = "testpassword"
incorrect_password = "wrongpassword"


@pytest.fixture
def test_client():
    """Создаем фикстуру для тестового клиента"""
    return client


# Тест 1: Успешная авторизация и получение токена
def test_successful_login(test_client):
    response = test_client.post(
        "/token",
        data={"username": test_username, "password": test_password}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "Bearer"


# Тест 2: Неуспешная авторизация с неверным паролем
def test_incorrect_password_login(test_client):
    response = test_client.post(
        "/token",
        data={"username": test_username, "password": incorrect_password}
    )
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"] == "Incorrect username or password"


# Тест 3: Получение данных текущего пользователя через заголовок Authorization
def test_get_current_user_via_header(test_client):
    # Сначала получаем токен
    login_response = test_client.post(
        "/token",
        data={"username": test_username, "password": test_password}
    )
    token = login_response.json()["access_token"]

    # Используем токен для запроса данных текущего пользователя
    response = test_client.get(
        "/me/head",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert "username" in response.json()
    assert response.json()["username"] == test_username


# Тест 4: Получение данных текущего пользователя через куки
def test_get_current_user_via_cookie(test_client):
    # Сначала получаем токен
    login_response = test_client.post(
        "/token",
        data={"username": test_username, "password": test_password}
    )
    token = login_response.json()["access_token"]

    # Устанавливаем куки на уровне клиента
    test_client.cookies.set("access_token", f"Bearer {token}")

    # Используем куки для запроса данных текущего пользователя
    response = test_client.get("/me/cookie")

    assert response.status_code == 200
    assert "username" in response.json()
    assert response.json()["username"] == test_username


# Тест 5: Получение данных текущего пользователя с некорректным токеном в заголовке
def test_get_current_user_invalid_token_via_header(test_client):
    invalid_token = "invalidtoken"
    response = test_client.get(
        "/me/head",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


# Тест 6: Получение данных текущего пользователя с некорректным токеном в куки
def test_get_current_user_invalid_token_via_cookie(test_client):
    invalid_token = "invalidtoken"

    # Устанавливаем некорректные куки на уровне клиента
    test_client.cookies.set("access_token", f"Bearer {invalid_token}")

    # Выполняем запрос с некорректными куки
    response = test_client.get("/me/cookie")

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
