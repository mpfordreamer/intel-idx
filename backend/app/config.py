from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized Application Configuration loaded from environment variables or .env file.
    Uses Pydantic v2 BaseSettings for type-safe validation.
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application Meta
    ENVIRONMENT: str = Field(default="development", description="Run environment (development/staging/production)")
    APP_NAME: str = Field(default="IDX-Intel AI", description="Application service name")
    DEBUG: bool = Field(default=True, description="Enable debug logging and tracebacks")
    PORT: int = Field(default=8002, description="HTTP API listening port")
    API_KEY_SECRET: str | None = Field(default=None, description="API Key for manual triggers")

    # Database & Cache Persistence
    DATABASE_URL: str = Field(
        description="Async SQLAlchemy database connection string",
    )
    REDIS_URL: str = Field(
        description="Redis connection URL for caching and rate limiting",
    )

    # LLM Provider Configuration
    LLM_PROVIDER: str = Field(default="orcarouter", description="LLM Provider Name")
    LLM_MODEL: str = Field(default="qwen/qwen3.8-27b-free", description="LLM Model string")
    LLM_MODEL_URL: str = Field(default="https://api.orcarouter.ai/v1", description="OpenAI compatible base URL")
    ORCAROUTER_API_KEY: str = Field(description="OrcaRouter API Key")
    OLLAMA_BASE_URL: str = Field(default="http://11.20.2.201:11434", description="Ollama API base URL")

    # WAHA (WhatsApp HTTP API) Configuration
    WAHA_BASE_URL: str = Field(default="http://localhost:3002", description="WAHA container base URL")
    WAHA_API_KEY: str = Field(description="X-Api-Key authentication header")
    WAHA_SESSION_ID: str = Field(default="default", description="WAHA WhatsApp session ID")
    WAHA_WEBHOOK_SECRET: str = Field(description="Webhook authentication secret")
    BROADCAST_CHAT_ID: str = Field(description="Target WhatsApp Group ID for alerts")
    ALWAYS_NOTIFY_WA: bool = Field(default=False, description="Send all events to WA regardless of category for testing")

    # Scheduler & Throttling
    SCRAPE_INTERVAL_MINUTES: int = Field(default=5, description="Interval for RSS and announcement scraping")
    RATE_LIMIT_COMMANDS_PER_MINUTE: int = Field(
        default=10, description="Max interactive WA commands per minute per phone number"
    )
    REDIS_CACHE_TTL_SECONDS: int = Field(
        default=600, description="TTL in seconds for summary and ticker cache (10 minutes)"
    )

    @property
    def WAHA_API_URL(self) -> str:
        return self.WAHA_BASE_URL

    @property
    def WAHA_SESSION(self) -> str:
        return self.WAHA_SESSION_ID


@lru_cache
def get_settings() -> Settings:
    """
    Singleton pattern for Settings instance using lru_cache.
    """
    return Settings()
