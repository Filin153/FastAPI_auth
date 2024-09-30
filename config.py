from FastAPI_auth.coder import JWTAuth, Hash


class FakeDB:
    def __init__(self):
        self.users = {
            'testuser': {'password': Hash.pwd_context.hash('testpassword')}
        }

    def get(self, filters: dict) -> dict | None:
        username = filters.get('username')
        if username in self.users:
            user = type('User', (), {})()  # Создаем объект User динамически
            user.username = username
            user.password = self.users[username]['password']
            return user
        return None


jwt_auth = JWTAuth("qweasdqwe", database=[FakeDB(), "get"])