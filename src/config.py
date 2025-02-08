"""Environment variables managing module"""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Env variables storing class"""
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    SECRET_KEY: str
    REF_TOK_LIFETIME_DAYS: int
    ACCS_TOK_LIFETIME_MIN: int
    BOOKS_LIMIT_FOR_READER: int

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
