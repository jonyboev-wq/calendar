from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    app_name: str = "Calendar Secretary"
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/calendar"
    timezone_default: str = "Europe/Helsinki"
    feature_caldav_enabled: bool = True
    feature_ics_enabled: bool = True
    objective_weight_priority: float = 1.0
    objective_weight_family_deficit: float = 3.0
    objective_weight_family_overuse: float = 2.0
    objective_weight_family_target: float = 1.0
    objective_bonus_pomodoro: float = 0.5
    secret_key: str = "change-me"
    encryption_key: str = Field(
        default=""  # to be populated via .env with Fernet key
    )

    class Config:
        env_file = str(Path(__file__).resolve().parents[2] / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("cors_origins", pre=True)
    def split_origins(cls, value: Any) -> list[str]:  # noqa: D401
        """Allow comma separated origins in .env files."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
