from sqlalchemy import MetaData, Table, Column, Integer, String, Float, DateTime

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