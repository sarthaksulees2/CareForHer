"""
PostgreSQL Database Configuration for MHM Hub
Database: careforher
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL connection string
# Format: postgresql://username:password@host:port/database
DATABASE_URL = "postgresql://postgres:root@localhost:5433/careforher"

# Create database engine
engine = create_engine(DATABASE_URL, echo=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Function to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to initialize database (create all tables)
def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
