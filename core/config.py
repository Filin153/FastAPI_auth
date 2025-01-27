from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8',
                                      extra="ignore")

    REDIS_HOST: str
    REDIS_PORT: int

    RABITMQ_HOST: str
    RABITMQ_PORT: int

    JWT_SECRET_KEY: str

    FERNET_KEY: str

    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    # database
    pg_user: str
    pg_pass: str
    pg_host: str
    pg_port: int
    pg_db_name: str

    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str

settings = Settings()