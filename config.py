from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "postgresql://testigo:testigo_pass@localhost:5432/testigo_db"
    api_port: int = 8000
    api_host: str = "0.0.0.0"
    debug: bool = True
    environment: str = "development"

    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    anthropic_api_key: Optional[str] = None
    llm_provider: str = "anthropic"
    llm_model: str = "claude-3-5-sonnet-20241022"

    redis_url: str = "redis://localhost:6379/0"

    consolidation_hour: int = 2
    consolidation_enabled: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
