from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        extra="ignore",
    )

    database_url: str = "sqlite:///./agrofarm.db"
    secret_key: str = "agrofarm-dev-secret-change-in-production"
    access_token_expire_minutes: int = 1440
    algorithm: str = "HS256"
    openweather_api_key: str = ""
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-20b"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    cors_origins: str = (
        "http://127.0.0.1:5173,http://localhost:5173,"
        "http://127.0.0.1:8000,http://localhost:8000"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def uploads_dir(self) -> Path:
        path = BACKEND_DIR / "uploads"
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
