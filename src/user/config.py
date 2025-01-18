import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

# Настройка базового логирования
logging.basicConfig(level=logging.DEBUG)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env',
                                      env_file_encoding='utf-8', extra='ignore')
    REDIS_HOST: str
    REDIS_PORT: int


def get_settings() -> Settings:
    settings = Settings()
    return settings


settings = get_settings()
