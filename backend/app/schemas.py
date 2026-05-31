from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any
from datetime import date, datetime
from decimal import Decimal

# --- Auth & User ---
class StudentBase(BaseModel):
    email: EmailStr
    full_name: str

class StudentCreate(StudentBase):
    password: str

class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    university_id: Optional[int] = None
    college_id: Optional[int] = None
    course_id: Optional[int] = None
    branch_id: Optional[int] = None
    current_semester: Optional[int] = None
    exam_date: Optional[date] = None
    daily_study_hours: Optional[float] = None

class StudentResponse(StudentBase):
    id: int
    university_id: Optional[int] = None
    college_id: Optional[int] = None
    course_id: Optional[int] = None
    branch_id: Optional[int] = None
    current_semester: Optional[int] = None
    exam_date: Optional[date] = None
    daily_study_hours: Optional[Decimal] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

# --- Curriculum & Academic context ---
class UniversityResponse(BaseModel):
    id: int
    name: str
    location: Optional[str] = None
    is_autonomous: bool

    class Config:
        from_attributes = True

class CollegeResponse(BaseModel):
    id: int
    name: str
    code: Optional[str] = None

    class Config:
        from_attributes = True

class CourseResponse(BaseModel):
    id: int
    name: str
    duration_semesters: int

    class Config:
        from_attributes = True

class BranchResponse(BaseModel):
    id: int
    name: str
    code: Optional[str] = None

    class Config:
        from_attributes = True

class SubjectResponse(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    semester: int

    class Config:
        from_attributes = True

class TopicResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

# --- PYQ Analyzer ---
class PYQResponse(BaseModel):
    id: int
    question_text: str
    answer_explanation: Optional[str] = None
    year: int
    month: Optional[str] = None
    marks: Optional[int] = None
    frequency_count: int
    difficulty_level: str

    class Config:
        from_attributes = True

class TopicFrequencyItem(BaseModel):
    topic_name: str
    question_count: int
    repeated_count: int
    percentage: float

class PYQAnalysisResponse(BaseModel):
    subject_id: int
    subject_name: str
    total_pyqs: int
    difficulty_distribution: dict # {"Easy": 3, "Medium": 2, "Hard": 5}
    important_topics: List[TopicFrequencyItem]
    repeated_questions: List[PYQResponse]

# --- AI Chat ---
class ChatMessage(BaseModel):
    role: str # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    topic_id: Optional[int] = None
    subject_id: int
    message: str
    history: List[ChatMessage] = []
    agent_role: Optional[str] = "orchestrator"

class ChatResponse(BaseModel):
    response: str
    suggested_pyqs: List[PYQResponse] = []

# --- AI Notes & Visual Notes ---
class NoteGenerateRequest(BaseModel):
    topic_id: Optional[int] = None
    custom_topic_name: Optional[str] = None
    subject_id: Optional[int] = None
    note_type: str # "Short Notes" | "Revision Notes" | "Detailed Explanation" | "Summary"

class NoteResponse(BaseModel):
    id: int
    topic_id: int
    note_type: str
    content_markdown: str
    created_at: datetime

    class Config:
        from_attributes = True

class VisualNoteGenerateRequest(BaseModel):
    topic_id: int
    visual_type: str # "Mindmap" | "Flowchart" | "Comparison Table"

class VisualNoteResponse(BaseModel):
    id: int
    topic_id: int
    visual_type: str
    structured_json: Any # Holds node/edge structure or tabular data
    created_at: datetime

    class Config:
        from_attributes = True

# --- Study Planner ---
class PlannerGenerateRequest(BaseModel):
    subject_id: int
    exam_date: date
    daily_study_hours: float

class StudyPlanCreate(BaseModel):
    subject_id: int
    topic_id: int
    scheduled_date: date
    duration_minutes: int

class StudyPlanUpdate(BaseModel):
    status: str # "Pending" | "Completed" | "Missed"

class StudyPlanResponse(BaseModel):
    id: int
    subject_id: int
    subject_name: str
    topic_id: int
    topic_name: str
    scheduled_date: date
    duration_minutes: int
    status: str

    class Config:
        from_attributes = True

# --- Tests Engine ---
class TestGenerateRequest(BaseModel):
    subject_id: int
    test_type: str # "MCQ" | "Short Answer" | "Long Practice" | "Timed Mock"
    topic_ids: Optional[List[int]] = None
    question_count: int = 5

class TestAnswerResponse(BaseModel):
    id: int
    question_text: str
    correct_answer: Optional[str] = None
    student_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    feedback: Optional[str] = None

    class Config:
        from_attributes = True

class TestResponse(BaseModel):
    id: int
    subject_id: int
    test_type: str
    score: Optional[float] = None
    total_questions: Optional[int] = None
    feedback_text: Optional[str] = None
    created_at: datetime
    questions: List[TestAnswerResponse] = []

    class Config:
        from_attributes = True

class StudentAnswerSubmission(BaseModel):
    question_id: int
    student_answer: str

class TestSubmitRequest(BaseModel):
    answers: List[StudentAnswerSubmission]
