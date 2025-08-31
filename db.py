from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, text
from sqlalchemy.sql import select, insert, update, delete
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"
if DEV_MODE:
    DATABASE_URL = os.getenv("DEV_DB_URL")
else:
    DATABASE_URL = os.getenv("PRODUCTION_DB_URL")

# Create engine
_db = create_engine(DATABASE_URL)
metadata = MetaData()

# Define tables
Users = Table(
    'users',
    metadata,
    Column('user_id', String, primary_key=True),
    Column('password', String, nullable=False),
    Column('name', String),
    Column('email', String),
    Column('role', String),
    Column('created_at', DateTime),
)

Courses = Table(
    'courses',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('course_code', String, nullable=False),
    Column('course_title', String),
    Column('course_unit', Integer),
    Column('lecturer_id', String),
    Column('semester', String),
    Column('session', String),
)

Student_Grade = Table(
    'student_grades',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('course_code', String, nullable=False),
    Column('lecturer_id', String),
    Column('student_id', String, nullable=False),
    Column('semester', String),
    Column('session', String),
    Column('course_unit', Integer),
    Column('ca_score', Integer),
    Column('exam_score', Integer),
    Column('total_score', Integer),
    Column('weight', Float),
    Column('letter_grade', String),
    Column('created_at', DateTime),
)

# Create tables if they don't exist
def create_tables():
    """Create all tables in the database"""
    try:
        metadata.create_all(_db)
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")

def execute(query):
    """Execute a query and return results"""
    with _db.connect() as conn:
        result = conn.execute(query)
        conn.commit()
        return result

# Optional: Create tables on import (remove if you handle this elsewhere)
# create_tables()