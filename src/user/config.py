import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

# Настройка базового логирования
logging.basicConfig(level=logging.DEBUG)


class Setting(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env',
                                      env_file_encoding='utf-8', extra='ignore')

    SECRET_KEY_FOR_JWT: str


def get_settings() -> Setting:
    settings = Setting()
    return settings


settings = get_settings()
