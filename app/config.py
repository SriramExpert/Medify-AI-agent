from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    OPENWEATHER_API_KEY: str
    OPENAI_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/agentic_db"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()