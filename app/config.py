"""
Central app configuration.

All settings are read from environment variables (via a .env file locally,
or real env vars in any deployed environment). Nothing here is hardcoded,
so the same code runs against local Postgres, a staging DB, or Round-2
infra without a single line changing.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ResolveAI Servicing Backend"
    environment: str = "development"

    # Postgres connection string, e.g.
    # postgresql+psycopg2://resolveai:resolveai@localhost:5432/resolveai_db
    database_url: str = "sqlite:///./resolveai_dev.db"

    # Redis connection string, e.g. redis://localhost:6379/0
    redis_url: str = "redis://localhost:6379/0"

    # Auto-approval thresholds — the policy engine reads these, not the AI layer.
    fee_reversal_max_amount: float = 500.0
    fee_reversal_min_account_age_months: int = 6
    credit_limit_max_auto_increase: float = 20000.0
    credit_limit_min_account_age_months: int = 12

    # Every servicing endpoint requires this header. In production this
    # would be per-caller (per-service or per-partner) tokens issued and
    # rotated through a real secrets manager, not a single shared value.
    internal_api_key: str = "change-me-in-production"


settings = Settings()
