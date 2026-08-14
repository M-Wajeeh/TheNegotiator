from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/negotiation"
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    OPENAI_API_KEY: str | None = None
    ELEVENLABS_API_KEY: str | None = None
    TAVILY_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    APP_URL: str | None = None
    GMAIL_SENDER_EMAIL: str | None = None
    GMAIL_CREDENTIALS_PATH: str | None = None
    SMTP_SERVER: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None

    model_config = SettingsConfigDict(
        env_file=(Path(__file__).resolve().parents[2] / ".env", Path(__file__).resolve().parents[1] / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
