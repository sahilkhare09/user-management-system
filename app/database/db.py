from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Database URL (from .env)
DATABASE_URL = settings.DATABASE_URL


# Connect to PostgreSQL using the URL in .env
engine = create_engine(DATABASE_URL)

# Create a session for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our database models
Base = declarative_base()


# Dependency for using DB in routers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
