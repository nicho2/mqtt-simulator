from __future__ import annotations

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment.

    References MQTT 3.1.1 \u00a73.1 CONNECT.
    """

    app_name: str = "MQTT Simulator"
    environment: str = "development"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
