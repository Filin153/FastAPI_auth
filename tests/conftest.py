import pytest
from requests import Session

from core.services.fernet import FernetService

test_session = Session()

@pytest.fixture()
def session():
    return test_session

@pytest.fixture()
def user_data():
    return {"email": "test@igoose.com", "password": "string"}

@pytest.fixture()
def fernet():
    return FernetService()

@pytest.fixture()
def base_path_to_api():
    return {
        "user": "http://localhost:1112/api/v1/users",
        "auth": "http://localhost:1111/api/v1/auth"
    }
