import secrets
from typing import Any


from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_COOKIE_NAME:str = secrets.token_urlsafe(32)
    REFRESH_TOKEN_COOKIE_NAME:str = secrets.token_urlsafe(32)
    REFRESH_TOKEN_SECRET_KEY: str = secrets.token_urlsafe(32)
    VERSION: str = "0.1.0"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60

    TOKEN_ALGORITHM:str = "HS256"

    PROJECT_NAME: str = "MONEY_HUB_BG3"
    SQLALCHEMY_DATABASE_URI: str = "postgresql+asyncpg://postgres:#$%RolaPss@localhost/virtual_wallet"
    PASSWORD_HASH_SALT:str = "MONEY_HUB"


settings = Settings()  # type: ignore
