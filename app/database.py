# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# Read DB URL from our Settings
SQLALCHEMY_DATABASE_URL = settings.database_url

# SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,      # shows SQL statements
    future=True,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

# Base class for ORM models
Base = declarative_base()


# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
