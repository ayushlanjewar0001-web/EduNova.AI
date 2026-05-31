from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Date, Numeric, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base

class University(Base):
    __tablename__ = "universities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    location = Column(String(255), nullable=True)
    is_autonomous = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    colleges = relationship("College", back_populates="university", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="university")

class College(Base):
    __tablename__ = "colleges"
    
    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    university = relationship("University", back_populates="colleges")
    students = relationship("Student", back_populates="college")

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    duration_semesters = Column(Integer, default=8)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    branches = relationship("Branch", back_populates="course", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="course")

class Branch(Base):
    __tablename__ = "branches"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    course = relationship("Course", back_populates="branches")
    subjects = relationship("Subject", back_populates="branch", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="branch")

class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="CASCADE"), nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=True)
    semester = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    branch = relationship("Branch", back_populates="subjects")
    university = relationship("University")
    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")
    pyqs = relationship("PYQ", back_populates="subject", cascade="all, delete-orphan")
    study_plans = relationship("StudyPlan", back_populates="subject", cascade="all, delete-orphan")
    tests = relationship("Test", back_populates="subject", cascade="all, delete-orphan")

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subject = relationship("Subject", back_populates="topics")
    pyqs = relationship("PYQ", back_populates="topic")
    study_plans = relationship("StudyPlan", back_populates="topic", cascade="all, delete-orphan")
    notes = relationship("GeneratedNote", back_populates="topic", cascade="all, delete-orphan")
    visual_notes = relationship("VisualNote", back_populates="topic", cascade="all, delete-orphan")

class PYQ(Base):
    __tablename__ = "pyqs"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    question_text = Column(Text, nullable=False)
    answer_explanation = Column(Text, nullable=True)
    year = Column(Integer, nullable=False)
    month = Column(String(50), nullable=True)
    marks = Column(Integer, nullable=True)
    frequency_count = Column(Integer, default=1)
    difficulty_level = Column(String(20), default="Medium")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subject = relationship("Subject", back_populates="pyqs")
    topic = relationship("Topic", back_populates="pyqs")

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=True)
    college_id = Column(Integer, ForeignKey("colleges.id"), nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    current_semester = Column(Integer, nullable=True)
    exam_date = Column(Date, nullable=True)
    daily_study_hours = Column(Numeric(3,1), default=2.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    university = relationship("University", back_populates="students")
    college = relationship("College", back_populates="students")
    course = relationship("Course", back_populates="students")
    branch = relationship("Branch", back_populates="students")
    
    study_plans = relationship("StudyPlan", back_populates="student", cascade="all, delete-orphan")
    notes = relationship("GeneratedNote", back_populates="student", cascade="all, delete-orphan")
    visual_notes = relationship("VisualNote", back_populates="student", cascade="all, delete-orphan")
    tests = relationship("Test", back_populates="student", cascade="all, delete-orphan")

class StudyPlan(Base):
    __tablename__ = "study_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    status = Column(String(20), default="Pending") # Pending, Completed, Missed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="study_plans")
    subject = relationship("Subject", back_populates="study_plans")
    topic = relationship("Topic", back_populates="study_plans")

class GeneratedNote(Base):
    __tablename__ = "generated_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    note_type = Column(String(20), nullable=False) # Short Notes, Revision Notes, Detailed Explanation, Summary
    content_markdown = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="notes")
    topic = relationship("Topic", back_populates="notes")

class VisualNote(Base):
    __tablename__ = "visual_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    visual_type = Column(String(20), nullable=False) # Mindmap, Flowchart, Comparison Table
    structured_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="visual_notes")
    topic = relationship("Topic", back_populates="visual_notes")

class Test(Base):
    __tablename__ = "tests"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    test_type = Column(String(20), nullable=False) # MCQ, Short Answer, Long Practice, Timed Mock
    score = Column(Numeric(5,2), nullable=True)
    total_questions = Column(Integer, nullable=True)
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="tests")
    subject = relationship("Subject", back_populates="tests")
    answers = relationship("TestAnswer", back_populates="test", cascade="all, delete-orphan")

class TestAnswer(Base):
    __tablename__ = "test_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=True)
    correct_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    test = relationship("Test", back_populates="answers")
