from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")

    database_url: str
    environment: str = "production"
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: float = 0.25
    jwt_refresh_expiration_days: int = 7
    max_login_attempts: int = 5
    login_attempt_window: int = 3600
    rate_limit_requests: int = 100
    rate_limit_period: int = 60
    min_transaction_amount: float = 0.01
    max_account_balance: float = 1000000.0

settings = Settings()
