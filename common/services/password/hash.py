from passlib.context import CryptContext


class Hash:
    # Контекст для работы с хешированием паролей с использованием bcrypt
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    # Метод для верификации пароля: сравнение plain-текста с хешем
    @classmethod
    async def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    # Метод для генерации хеша пароля
    @classmethod
    async def get_password_hash(cls, password):
        return cls.pwd_context.hash(password)