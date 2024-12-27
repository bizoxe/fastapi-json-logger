"""
Main application settings.
"""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

BASE_DIR = Path(__file__).parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    public: str = "/public"


class ApiBaseConfig(BaseModel):
    name: str = "Asynchronous json logger for FastAPI"
    version: str = "1.0"
    prefix: str = "/api"
    environment: str = "dev"
    v1: ApiV1Prefix = ApiV1Prefix()


class LoggingBaseConfig(BaseModel):
    log_dir: Path = BASE_DIR.joinpath("logs")
    log_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"
    to_file: bool = True
    default_log_cfg_yaml: Path = BASE_DIR / "default_logger_cfg.yaml"
    patterns: tuple[str, ...] = (
        "credentials",
        "authorization",
        "token",
        "secret",
        "password",
        "access",
    )
    pass_routes: tuple[str, ...] = (
        "/openapi.json",
        "/docs",
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            ".env.template",
            ".env",
        ),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    log_cfg: LoggingBaseConfig = LoggingBaseConfig()
    api: ApiBaseConfig = ApiBaseConfig()


settings = Settings()
