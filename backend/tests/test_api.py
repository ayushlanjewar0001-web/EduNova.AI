import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.models import (
    University, Course, Branch, Subject, Topic, PYQ, Student, 
    StudyPlan, GeneratedNote, VisualNote, Test, TestAnswer
)

import os

# Local database file for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    try:
        # Seed test database items
        univ = University(id=1, name="Test University of Mumbai", location="Mumbai", is_autonomous=False)
        course = Course(id=1, name="Test B.Tech", duration_semesters=8)
        branch = Branch(id=1, course_id=1, name="Test CSE", code="CSE")
        subject = Subject(id=1, branch_id=1, semester=5, name="Test DBMS", code="CS501")
        topic = Topic(id=1, subject_id=1, name="Test Normalization", description="Desc")
        pyq = PYQ(
            subject_id=1,
            topic_id=1,
            question_text="Explain BCNF with a suitable example.",
            answer_explanation="BCNF is Boyce-Codd Normal Form...",
            year=2023,
            month="May",
            marks=10,
            frequency_count=4,
            difficulty_level="Medium"
        )
        db_session.add_all([univ, course, branch, subject, topic, pyq])
        db_session.commit()
        yield db_session
    finally:
        db_session.close()
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("test.db"):
            try:
                os.remove("test.db")
            except PermissionError:
                pass

@pytest.fixture(scope="module")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to EduNova.AI Backend API"}

def test_register_student(client):
    register_data = {
        "email": "teststudent@edunova.ai",
        "password": "strongpassword123",
        "full_name": "Ayush Maharashtra"
    }
    response = client.post("/api/auth/register", json=register_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "teststudent@edunova.ai"
    assert data["full_name"] == "Ayush Maharashtra"
    assert "id" in data

def test_login_student(client):
    # Retrieve access token
    login_data = {
        "username": "teststudent@edunova.ai",
        "password": "strongpassword123"
    }
    response = client.post("/api/auth/token", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_universities(client):
    response = client.get("/api/curriculum/universities")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Test University of Mumbai"

def test_get_subjects(client):
    response = client.get("/api/curriculum/subjects?branch_id=1&semester=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test DBMS"

def test_ai_teacher_chat_unauthorized(client):
    chat_payload = {
        "subject_id": 1,
        "message": "Explain BCNF",
        "history": []
    }
    response = client.post("/api/ai/teacher/chat", json=chat_payload)
    # Should fail with 401 because no Authorization header is provided
    assert response.status_code == 401

def test_ai_teacher_chat_with_agents(client):
    # 1. Login to get token
    login_data = {
        "username": "teststudent@edunova.ai",
        "password": "strongpassword123"
    }
    login_resp = client.post("/api/auth/token", data=login_data)
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test Orchestrator Agent
    chat_payload_orchestrator = {
        "subject_id": 1,
        "message": "Explain Database Normalization",
        "history": [],
        "agent_role": "orchestrator"
    }
    response = client.post("/api/ai/teacher/chat", json=chat_payload_orchestrator, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "[AGENT_THOUGHTS]" in data["response"]
    assert "Coordinator Agent" in data["response"]

    # 3. Test Professor Agent
    chat_payload_prof = {
        "subject_id": 1,
        "message": "Explain Database Normalization",
        "history": [],
        "agent_role": "professor"
    }
    response = client.post("/api/ai/teacher/chat", json=chat_payload_prof, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "Professor's Lecture" in data["response"]

    # 4. Test Examiner Agent
    chat_payload_exam = {
        "subject_id": 1,
        "message": "Give me a quiz",
        "history": [],
        "agent_role": "examiner"
    }
    response = client.post("/api/ai/teacher/chat", json=chat_payload_exam, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "Examiner's Assessment" in data["response"]

