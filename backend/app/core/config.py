"""Typed application settings, loaded from environment variables (twelve-factor, Doc 9.1)."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["local", "test", "staging", "production"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # No defaults: the app must fail fast if these are not configured.
    database_url: str
    redis_url: str

    # Seconds allowed for each dependency check in /ready.
    readiness_timeout_s: float = 2.0


@lru_cache
def get_settings() -> Settings:
    return Settings()  # values come from the environment
