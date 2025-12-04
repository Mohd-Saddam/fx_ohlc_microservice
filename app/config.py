"""
Application configuration using Pydantic Settings.

Centralizes configuration with environment variable support and type validation.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    Loads configuration from environment variables, provides defaults,
    and validates types to prevent runtime configuration errors.
    """
    
    # Database Configuration - TimescaleDB connection parameters
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "fxohlc"
    
    # Redis Configuration - Pub/Sub for event-driven tick distribution
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://redis:6379"
    REDIS_PASSWORD: Optional[str] = None
    
    # Application Configuration
    TICK_CHANNEL: str = "eurusd_ticks"  # Redis channel for tick streaming
    LOG_LEVEL: str = "INFO"  # Logging verbosity (DEBUG/INFO/WARNING/ERROR)
    
    # API Configuration - Displayed in Swagger UI
    API_TITLE: str = "FX OHLC Microservice"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Production-ready microservice for real-time FX OHLC data"
    
    # Performance Settings - Database connection pooling to prevent connection overhead
    DB_POOL_SIZE: int = 20  # Max connections in pool
    DB_MAX_OVERFLOW: int = 40  # Additional connections beyond pool_size
    DB_POOL_RECYCLE: int = 3600  # Recycle connections after 1 hour to prevent stale connections
    
    @property
    def database_url(self) -> str:
        """Async database URL using asyncpg driver for non-blocking I/O."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def database_url_sync(self) -> str:
        """Sync database URL for initial setup operations (CREATE EXTENSION, etc.)."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self. POSTGRES_HOST}:{self. POSTGRES_PORT}/{self. POSTGRES_DB}"
        )
    
    @property
    def redis_url_with_auth(self) -> str:
        """Redis URL with optional authentication for production environments."""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
        return self.REDIS_URL
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()