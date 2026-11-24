"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # App
    APP_ENV: str = "development"
    CORS_ORIGINS: str = "https://everafter-heart-login.lovable.app"

    # Token TTLs (seconds)
    ACCESS_TOKEN_TTL: int = 3600            # 1 hour
    REFRESH_TOKEN_TTL: int = 604800         # 7 days
    REFRESH_TOKEN_TTL_REMEMBER: int = 2592000  # 30 days

    # OTP
    OTP_TTL: int = 300
    OTP_MAX_ATTEMPTS: int = 3

    # Rate limits per minute
    RATE_LOGIN: int = 5
    RATE_OTP: int = 5
    RATE_PASSWORD: int = 5

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()