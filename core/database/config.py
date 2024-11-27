from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env',
                                      env_file_encoding='utf-8', extra='ignore')

    # database
    pg_user: str
    pg_pass: str
    pg_host: str
    pg_port: int
    pg_db_name: str


def get_db_url_async() -> str:
    settings = Setting()
    return f"postgresql+asyncpg://{settings.pg_user}:{settings.pg_pass}@{settings.pg_host}:{settings.pg_port}/{settings.pg_db_name}"

def get_db_url_sync() -> str:
    settings = Setting()
    return f"postgresql://{settings.pg_user}:{settings.pg_pass}@{settings.pg_host}:{settings.pg_port}/{settings.pg_db_name}"
