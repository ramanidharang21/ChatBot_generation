from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "Ghostwriter API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # AWS SETTINGS - Added credential fields
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_SESSION_TOKEN: Optional[str] = None # Critical for SSO/Temporary sessions

    BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"

    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 3000

    class Config:
        env_file = ".env"
        extra = "ignore" # Allows extra env vars without crashing

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()