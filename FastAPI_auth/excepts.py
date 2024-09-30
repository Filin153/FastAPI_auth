from fastapi import HTTPException  # Импорт FastAPI исключений для возврата HTTP ошибок


# Класс исключения, выбрасываемого при отсутствии метода "get" в объекте базы данных
class DatabaseObjectNoGetMethod(Exception):
    def __init__(self, http: bool = False):
        """
        :param http: Если True, генерируется HTTPException для обработки в FastAPI, иначе обычное исключение.
        """
        if http:
            # Если параметр http=True, выбрасывается HTTPException с кодом 500 (внутренняя ошибка сервера)
            raise HTTPException(status_code=500, detail="Database object has no get method")

        # В остальных случаях выбрасывается обычное исключение с соответствующим сообщением
        super().__init__("Database object has no get method")


# Класс исключения, выбрасываемого, если пользователь не найден
class UserNotFound(Exception):
    def __init__(self, http: bool = False):
        """
        :param http: Если True, генерируется HTTPException с кодом 401, иначе обычное исключение.
        """
        if http:
            # Если параметр http=True, выбрасывается HTTPException с кодом 401 (не авторизован)
            raise HTTPException(status_code=401, detail="User does not exist")

        # В остальных случаях выбрасывается обычное исключение с сообщением "User does not exist"
        super().__init__("User does not exist")


# Класс исключения, выбрасываемого при некорректном пароле
class IncorrectPassword(Exception):
    def __init__(self, http: bool = False):
        """
        :param http: Если True, генерируется HTTPException с кодом 401, иначе обычное исключение.
        """
        if http:
            # Если параметр http=True, выбрасывается HTTPException с кодом 401 (не авторизован)
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        # В остальных случаях выбрасывается обычное исключение с сообщением "Incorrect username or password"
        super().__init__("Incorrect username or password")
