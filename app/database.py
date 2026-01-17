import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Loading files from .env file
load_dotenv()

# Get the URL from environment variables
DATABASE_URL = os.getenv('DATABASE_URL')

# --- FIX FOR RENDER/SQLAlchemy 2.0 compatibility ---
# SQLAlchemy 2.0 removed support for the 'postgres://' prefix. 
# We must ensure it is 'postgresql://'
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
# ----------------------------------------------------

# Creating an engine
# Note: For Postgres, we don't need 'check_same_thread'
engine = create_engine(DATABASE_URL)

# CREATING SESSIONLOCAL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# CREATING BASE
BASE = declarative_base()

# CREATING DATABASE DEPENDENCY
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()