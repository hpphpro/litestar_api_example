import os
from pathlib import Path
from typing import (
    Final,
    Literal,
)

from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal[
    "CRITICAL", "FATAL", "ERROR", "WARN", "WARNING", "INFO", "DEBUG", "NOTSET"
]
_PathLike = os.PathLike[str] | str | Path

LOGGING_FORMAT: Final[str] = "%(asctime)s %(name)s %(levelname)s -> %(message)s"
DATETIME_FORMAT: Final[str] = "%Y.%m.%d %H:%M"


def root_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def path(*paths: _PathLike, base_path: _PathLike | None = None) -> str:
    if base_path is None:
        base_path = root_dir()

    return os.path.join(base_path, *paths)


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="DB_",
        extra="ignore",
    )

    driver: str = ""
    name: str = ""
    host: str | None = None
    port: int | None = None
    user: str | None = None
    password: str | None = None
    connection_pool_size: int = 10
    connection_max_overflow: int = 90
    connection_pool_pre_ping: bool = True
    max_connections: int = 100  # postgres default

    @property
    def url(self) -> str:
        if "sqlite" in self.driver:
            return f"{self.driver}://{self.name}"

        return f"{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="SERVER_",
        extra="ignore",
    )
    log_level: LogLevel = "INFO"
    cors: int = 1
    cors_methods: list[
        Literal[
            "*", "GET", "POST", "DELETE", "PATCH", "PUT", "HEAD", "TRACE", "OPTIONS"
        ]
    ] = ["*"]
    cors_headers: list[str] = ["*"]
    cors_origins: list[str] = ["*"]
    cors_expose_headers: list[str] = []
    csrf_secret: str = ""
    title: str | None = None
    debug: int = 1
    version: str = "0.0.1"
    host: str = "127.0.0.1"
    port: int = 8080
    type: Literal["granian", "uvicorn", "gunicorn"] = "granian"
    domain: str = "http://localhost:8080"


class CipherSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="CIPHER_",
        extra="ignore",
    )
    aes_key: str = ""
    algorithm: str = ""
    secret_key: str = ""
    public_key: str = ""
    access_token_expire_seconds: int = 0
    refresh_token_expire_seconds: int = 0


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="REDIS_",
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = 6379
    password: str | None = None


class Settings(BaseSettings):
    server: ServerSettings
    db: DatabaseSettings
    cipher: CipherSettings
    redis: RedisSettings


def load_settings(
    server: ServerSettings | None = None,
    db: DatabaseSettings | None = None,
    cipher: CipherSettings | None = None,
    redis: RedisSettings | None = None,
) -> Settings:
    return Settings(
        server=server or ServerSettings(),
        db=db or DatabaseSettings(),
        cipher=cipher or CipherSettings(),
        redis=redis or RedisSettings(),
    )
