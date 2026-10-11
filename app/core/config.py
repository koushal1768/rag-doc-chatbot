import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "RAG Multi-Tenant Platform"
    
    # System Default API Keys (Fallback if user does not provide BYOK)
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()