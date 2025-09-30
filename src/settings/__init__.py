from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # General
    environment: Literal["develop", "staging", "production"] = "develop"
    database_url: str = "sqlite:///:memory:"


settings = Settings()
