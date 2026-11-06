from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables and ``.env``."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    api_host: str = "127.0.0.1"
    api_port: int = 8000
    database_url: str = "postgresql+asyncpg://oracle_flow:oracle_flow@localhost:5432/oracle_flow"
    cors_origins: list[str] = ["http://localhost:3000"]
    gemini_api_key: str | None = None
    llm_model_id: str = "gemini-2.5-flash"
    rate_limit_per_minute: int = 60


settings = Settings()

API_HOST = settings.api_host
API_PORT = settings.api_port
API_URL = f"http://{API_HOST}:{API_PORT}"

GEMINI_API_KEY = settings.gemini_api_key
LLM_MODEL_ID = settings.llm_model_id

MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 8.0
