from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Gemini settings
    GEMINI_API_KEY: str
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "english_server_db"
    
    # Schema synchronization settings
    AUTO_SYNC_SCHEMA: bool = True
    AUTO_CREATE_COLLECTIONS: bool = True
    AUTO_UPDATE_INDEXES: bool = True
    AUTO_UPDATE_VALIDATION: bool = True
    
    # Server settings
    ENV: str = "development"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields from .env

settings = Settings()
