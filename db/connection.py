from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from .models import metadata

load_dotenv()

# Database connection
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"
if DEV_MODE:
    DATABASE_URL = os.getenv("DEV_DB_URL")
else:
    DATABASE_URL = os.getenv("PRODUCTION_DB_URL")

# Create engine
_db = create_engine(DATABASE_URL)

def execute(query):
    """Execute a query and return results"""
    with _db.connect() as conn:
        result = conn.execute(query)
        conn.commit()
        return result

def create_tables():
    """Create all tables in the database"""
    try:
        metadata.create_all(_db)
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")