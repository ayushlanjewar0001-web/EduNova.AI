import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "EduNova.AI"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "edunova_super_secret_key_change_me_in_production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Fallback to sqlite if postgres URL not provided
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./edunova.db"
    )
    
    class Config:
        case_sensitive = True

settings = Settings()
