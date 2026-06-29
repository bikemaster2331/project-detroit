from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "Project Detroit"
    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'detroit.db'}"
    autonomy_enabled: bool = True
    autonomy_tick_seconds: int = 30
    autonomy_cooldown_minutes: int = 5
    max_initiations_per_day: int = 5

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
