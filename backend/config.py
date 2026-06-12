import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # API key for Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
    
    # SQLite local file path
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./interview_system.db")
    
    # Gemini model target
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Demo Mode setting
    # Defaults to True if GEMINI_API_KEY is empty, allowing out-of-the-box local testing
    DEMO_MODE_ENV = os.getenv("DEMO_MODE", "").lower()
    DEMO_MODE: bool = DEMO_MODE_ENV in ("true", "1", "yes") or not GEMINI_API_KEY

settings = Settings()
