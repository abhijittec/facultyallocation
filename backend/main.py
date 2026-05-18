from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:////tmp/faculty_allocation.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- DATA MODELS ---
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
    intake_sections = Column(Integer, default=2)

class Preference(Base):
    __tablename__ = "preferences"
    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(Integer, ForeignKey("faculty.id", ondelete="CASCADE"))
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
    priority = Column(Integer, nullable=False) # 1, 2, or 3

    __table_args__ = (
        UniqueConstraint('faculty_id', 'subject_id', name='_faculty_sub_uc'),
        UniqueConstraint('faculty_id', 'priority', name='_faculty_prio_uc'),
    )

Base.metadata.create_all(bind=engine)

# --- FASTAPI APP ---
app = FastAPI(title="Faculty Allocation System Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/seed-data/")
def seed_data(db: Session = Depends(get_db)):
    db.query(Preference).delete()
    db.query(Subject).delete()
    db.query(Faculty).delete()
    db.commit()
    
    # 1. Seed 25 Faculty Members
    faculties = [
        Faculty(name=f"Dr. Professor Alpha {i}", email=f"faculty{i}@university.edu")
        for i in range(1, 26)
    ]
    db.add_all(faculties)
    
    # 2. Seed 50 Diverse Subjects across 8 Semesters
    subjects_pool = [
        # Sem 1
        Subject(subject_code="SUB101", subject_name="Engineering Mathematics I", semester=1, intake_sections=2),
        Subject(subject_code="SUB102", subject_name="Applied Physics", semester=1, intake_sections=2),
        Subject(subject_code="SUB103", subject_name="Programming Basics in C", semester=1, intake_sections=3),
        Subject(subject_code="SUB104", subject_name="Professional Communication", semester=1, intake_sections=2),
        Subject(subject_code="SUB105", subject_name="Basic Mechanical Systems", semester=1, intake_sections=2),
        Subject(subject_code="SUB106", subject_name="Environmental Engineering", semester=1, intake_sections=1),
        # Sem 2
        Subject(subject_code="SUB201", subject_name="Engineering Mathematics II", semester=2, intake_sections=2),
        Subject(subject_code="SUB202", subject_name="Engineering Chemistry", semester=2, intake_sections=2),
        Subject(subject_code="SUB203", subject_name="Basic Electrical Engineering", semester=2, intake_sections=3),
        Subject(subject_code="SUB204", subject_name="Engineering Graphics & Mechanics", semester=2, intake_sections=2),
        Subject(subject_code="SUB205", subject_name="Data Structures Lab", semester=2, intake_sections=2),
        Subject(subject_code="SUB206", subject_name="Workshop Practices", semester=2, intake_sections=1),
        # Sem 3
        Subject(subject_code="SUB301", subject_name="Data Structures and Algorithms", semester=3, intake_sections=2),
        Subject(subject_code="SUB302", subject_name="Operating Systems Concepts", semester=3, intake_sections=2),
        Subject(subject_code="SUB303", subject_name="Digital Logic Principles", semester=3, intake_sections=2),
        Subject(subject_code="SUB304", subject_name="Discrete Mathematics Foundations", semester=3, intake_sections=2),
        Subject(subject_code="SUB305", subject_name="Object Oriented Paradigm", semester=3, intake_sections=3),
        Subject(subject_code="SUB306", subject_name="Signals and Systems Infrastructure", semester=3, intake_sections=1),
        # Sem 4
        Subject(subject_code="SUB401", subject_name="Database Management Systems", semester=4, intake_sections=2),
        Subject(subject_code="SUB402", subject_name="Computer Architecture Systems", semester=4, intake_sections=2),
        Subject(subject_code="SUB403", subject_name="Formal Languages & Automata", semester=4, intake_sections=2),
        Subject(subject_code="SUB404", subject_name="Design and Analysis of Algorithms", semester=4, intake_sections=2),
        Subject(subject_code="SUB405", subject_name="Microprocessors Architecture", semester=4, intake_sections=2),
        Subject(subject_code="SUB406", subject_name="Probability and Random Processes", semester=4, intake_sections=1),
        # Sem 5
        Subject(subject_code="SUB501", subject_name="Computer Network Engineering", semester=5, intake_sections=2),
        Subject(subject_code="SUB502", subject_name="Software Engineering Methodologies", semester=5, intake_sections=2),
        Subject(subject_code="SUB503", subject_name="Artificial Intelligence Core", semester=5, intake_sections=2),
        Subject(subject_code="SUB504", subject_name="Web Application Architectures", semester=5, intake_sections=3),
        Subject(subject_code="SUB505", subject_name="Optimization Techniques Matrix", semester=5, intake_sections=2),
        Subject(subject_code="SUB506", subject_name="System Programming Mechanics", semester=5, intake_sections=1),
        # Sem 6
        Subject(subject_code="SUB601", subject_name="Machine Learning Paradigms", semester=6, intake_sections=2),
        Subject(subject_code="SUB602", subject_name="Compiler Design Implementations", semester=6, intake_sections=2),
        Subject(subject_code="SUB603", subject_name="Cryptography & System Security", semester=6, intake_sections=2),
        Subject(subject_code="SUB604", subject_name="Cloud Computing Environments", semester=6, intake_sections=3),
        Subject(subject_code="SUB605", subject_name="Data Warehousing & Data Mining", semester=6, intake_sections=2),
        Subject(subject_code="SUB606", subject_name="Embedded Systems Design", semester=6, intake_sections=1),
        # Sem 7
        Subject(subject_code="SUB701", subject_name="Distributed Operating Architectures", semester=7, intake_sections=2),
        Subject(subject_code="SUB702", subject_name="Deep Learning & Neural Matrix", semester=7, intake_sections=2),
        Subject(subject_code="SUB703", subject_name="Big Data Frameworks & Systems", semester=7, intake_sections=2),
        Subject(subject_code="SUB704", subject_name="Internet of Things Integrations", semester=7, intake_sections=2),
        Subject(subject_code="SUB705", subject_name="Mobile Computing Topologies", semester=7, intake_sections=2),
        Subject(subject_code="SUB706", subject_name="Software Project Management", semester=7, intake_sections=1),
        # Sem 8
        Subject(subject_code="SUB801", subject_name="Cyber Forensics & Digital Laws", semester=8, intake_sections=2),
        Subject(subject_code="SUB802", subject_name="Natural Language Processing Core", semester=8, intake_sections=2),
        Subject(subject_code="SUB803", subject_name="Human Computer Interaction Layouts", semester=8, intake_sections=2),
        Subject(subject_code="SUB804", subject_name="Blockchain Consensus Networks", semester=8, intake_sections=2),
        Subject(subject_code="SUB805", subject_name="Parallel Computing Nodes", semester=8, intake_sections=2),
        Subject(subject_code="SUB806", subject_name="Green Computing Topologies", semester=8, intake_sections=1),
        Subject(subject_code="SUB807", subject_name="Quantum Computing Fundamentals", semester=8, intake_sections=1),
        Subject(subject_code="SUB808", subject_name="Virtual Reality Simulation Interfaces", semester=8, intake_sections=1)
    ]
    
    db.add_all(subjects_pool)
    db.commit()
    return {"message": "Reset and seeded exactly 25 Faculty members and 50 subjects across 8 Semesters!"}

@app.get("/subjects/available/")
def get_available_subjects(db: Session = Depends(get_db)):
    all_subjects = db.query(Subject).all()
    available_list = []
    for s in all_subjects:
        taken_count = db.query(Preference).filter(Preference.subject_id == s.id).count()
        if taken_count < s.intake_sections:
            available_list.append(s)
    return available_list

@app.get("/faculty-list/")
def get_faculty(db: Session = Depends(get_db)):
    return db.query(Faculty).all()

# Master Analytics Endpoint: Who has chosen what?
@app.get("/preferences/master-report/")
def get_master_preference_report(db: Session = Depends(get_db)):
    records = db.query(Preference).all()
    report = []
    for r in records:
        f = db.query(Faculty).filter(Faculty.id == r.faculty_id).first()
        s = db.query(Subject).filter(Subject.id == r.subject_id).first()
        if f and s:
            report.append({
                "faculty_name": f.name,
                "faculty_email": f.email,
                "subject_code": s.subject_code,
                "subject_name": s.subject_name,
                "semester": s.semester,
                "priority": r.priority
            })
    return report

class PreferenceSubmission(BaseModel):
    faculty_id: int
    first_choice_id: int
    second_choice_id: int
    third_choice_id: int

@app.post("/submit-preferences/")
def save_preferences(data: PreferenceSubmission, db: Session = Depends(get_db)):
    for s_id in [data.first_choice_id, data.second_choice_id, data.third_choice_id]:
        subject = db.query(Subject).filter(Subject.id == s_id).first()
        if not subject:
            raise HTTPException(status_code=400, detail="Invalid subject selection.")
        taken_count = db.query(Preference).filter(Preference.subject_id == s_id).count()
        if taken_count >= subject.intake_sections:
            raise HTTPException(status_code=400, detail=f"[{subject.subject_name}] is no longer available.")
            
    db.query(Preference).filter(Preference.faculty_id == data.faculty_id).delete()
    p1 = Preference(faculty_id=data.faculty_id, subject_id=data.first_choice_id, priority=1)
    p2 = Preference(faculty_id=data.faculty_id, subject_id=data.second_choice_id, priority=2)
    p3 = Preference(faculty_id=data.faculty_id, subject_id=data.third_choice_id, priority=3)
    db.add_all([p1, p2, p3])
    db.commit()
    return {"status": "success"}

@app.post("/allocate/")
def run_allocation(db: Session = Depends(get_db)):
    faculties = db.query(Faculty).all()
    subjects = db.query(Subject).all()
    preferences = db.query(Preference).all()

    faculty_workload = {f.id: 0 for f in faculties}
    subject_capacity = {s.id: s.intake_sections for s in subjects}
    final_allocations = []

    for current_priority in [1, 2, 3]:
        round_prefs = [p for p in preferences if p.priority == current_priority]
        for pref in round_prefs:
            if faculty_workload[pref.faculty_id] >= 2:
                continue
            if subject_capacity[pref.subject_id] > 0:
                f_obj = db.query(Faculty).filter(Faculty.id == pref.faculty_id).first()
                s_obj = db.query(Subject).filter(Subject.id == pref.subject_id).first()
                final_allocations.append({
                    "faculty_id": pref.faculty_id,
                    "faculty_name": f_obj.name if f_obj else f"ID {pref.faculty_id}",
                    "subject_id": pref.subject_id,
                    "subject_name": s_obj.subject_name if s_obj else f"ID {pref.subject_id}",
                    "priority_matched": current_priority
                })
                faculty_workload[pref.faculty_id] += 1
                subject_capacity[pref.subject_id] -= 1

    return {"status": "success", "allocations": final_allocations}