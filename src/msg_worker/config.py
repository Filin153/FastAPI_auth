from pydantic_settings import BaseSettings, SettingsConfigDict
import pathlib

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=f"{pathlib.Path(__file__).parent.absolute()}/.env",
                                  env_file_encoding="utf-8", extra='ignore')

    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str

settings = Settings()