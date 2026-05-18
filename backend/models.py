from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from database import Base

class Faculty(Base):
    __tablename__ = "faculty"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    subject_code = Column(String, unique=True, nullable=False)
    subject_name = Column(String, nullable=False)
    semester = Column(Integer, nullable=False)
    intake_sections = Column(Integer, default=1)

class Preference(Base):
    __tablename__ = "preferences"
    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(Integer, ForeignKey("faculty.id", ondelete="CASCADE"))
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
    priority = Column(Integer, nullable=False) # 1, 2, or 3

    # Constraints to prevent duplicate subject choices per faculty
    __table_args__ = (
        UniqueConstraint('faculty_id', 'subject_id', name='_faculty_subject_uc'),
        UniqueConstraint('faculty_id', 'priority', name='_faculty_priority_uc'),
    )