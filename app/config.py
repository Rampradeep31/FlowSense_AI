from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "FlowSense AI"
    APP_VERSION: str = "v1"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # Database Settings
    # Defaults to local async SQLite. In production/Docker, this will be PostgreSQL.
    DATABASE_URL: str = "sqlite+aiosqlite:///./flowsense.db"

    # Redis Caching Settings
    # If None, the cache service falls back to in-memory Python dictionary caching.
    REDIS_URL: Optional[str] = None

    # External API Keys (OpenWeather and NewsAPI)
    # If missing, services fall back to simulated/mock data.
    OPENWEATHER_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None

    # OSRM (OpenStreetMap Routing Machine) Settings
    # Default to public OSRM demo server. If offline, service falls back to geographic estimation.
    OSRM_BASE_URL: str = "https://router.project-osrm.org"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
