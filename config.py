from FastAPI_auth.coder import Hash


class FakeDB:
    def __init__(self):
        self.users = {
            'testuser': {'password': Hash.pwd_context.hash('testpassword')}
        }

    async def get(self, filters: dict) -> dict | None:
        username = filters.get('username')
        if username in self.users:
            user = type('User', (), {})()  # Создаем объект User динамически
            user.username = username
            user.password = self.users[username]['password']
            user.totp_secret = None
            return user
        return None