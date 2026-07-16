import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "flowsense-procurement-secret-key-btech-miniproject")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # Default 24 hours
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./flowsense_procurement.db")

settings = Settings()
