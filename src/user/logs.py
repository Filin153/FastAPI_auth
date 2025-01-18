import logging

# Настройка логирования
def setup_logging():
    # Создаем логгер
    logger = logging.getLogger("uvicorn")
    logger.setLevel(logging.INFO)

    # Создаем обработчики для вывода в консоль и в файл
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("logs.txt")

    # Формат логов
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Добавляем обработчики к логгеру
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger