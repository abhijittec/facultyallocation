from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use local SQLite database file
SQLALCHEMY_DATABASE_URL = "sqlite:///./faculty_allocation.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get database session helper
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()