import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    APP_NAME: str = "OCR API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    ALLOWED_ORIGINS: list = ["*"]
    
    # OCR Settings
    OCR_LANGUAGES: list = ["en"]
    OCR_GPU: bool = False
    
    # API Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()