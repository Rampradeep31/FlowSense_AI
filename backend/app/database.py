import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Database URL from environment, fallback to SQLite for local development convenience
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./flowsense_procurement.db")

# Fix for PostgreSQL or SQLite async URL formats if needed
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
if "sqlite+aiosqlite" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")
if "postgresql+asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

# Configure connection arguments based on DB engine type
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create Engine
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

# Configure Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base
Base = declarative_base()

# DB Dependency injection helper
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
