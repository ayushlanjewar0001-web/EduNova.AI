from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Any
import json

from app.core.database import get_db
from app.api.auth import get_current_student
from app.models import Student, Subject, Topic, PYQ, GeneratedNote, VisualNote, StudyPlan
from app.schemas import (
    ChatRequest, ChatResponse, PYQAnalysisResponse, TopicFrequencyItem, PYQResponse,
    NoteGenerateRequest, NoteResponse, VisualNoteGenerateRequest, VisualNoteResponse,
    StudyPlanResponse, PlannerGenerateRequest, StudyPlanUpdate
)
from app.services.ai_service import AIService

router = APIRouter()

@router.post("/teacher/chat", response_model=ChatResponse)
def chat_with_teacher(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student)
):
    """
    Interact with the AI Teacher, incorporating topic and PYQ context.
    """
    subject = db.query(Subject).filter(Subject.id == request.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
        
    topic_name = ""
    pyqs = []
    if request.topic_id:
        topic = db.query(Topic).filter(Topic.id == request.topic_id).first()
        if topic:
            topic_name = topic.name
            pyqs = db.query(PYQ).filter(PYQ.topic_id == topic.id).all()
            
    if not pyqs:
        pyqs = db.query(PYQ).filter(PYQ.subject_id == request.subject_id).all()
        
    chat_data = AIService.generate_chat_response(
        query=request.message,
        subject_name=subject.name,
        topic_name=topic_name,
        pyqs=pyqs,
        agent_role=request.agent_role
    )
    return ChatResponse(**chat_data)

@router.get("/pyq-analyzer/{subject_id}", response_model=PYQAnalysisResponse)
def analyze_pyqs(subject_id: int, db: Session = Depends(get_db)):
    """
    Analyze past year questions for the specified subject.
    Provides difficulty distributions, repetition count, and high-yield topics.
    """
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
        
    pyqs = db.query(PYQ).filter(PYQ.subject_id == subject_id).all()
    
    # Calculate difficulty distribution
    difficulty_dist = {"Easy": 0, "Medium": 0, "Hard": 0}
    for pyq in pyqs:
        diff = pyq.difficulty_level or "Medium"
        if diff in difficulty_dist:
            difficulty_dist[diff] += 1
            
    # Calculate important topics based on frequency counts of questions
    topics = db.query(Topic).filter(Topic.subject_id == subject_id).all()
    topic_items = []
    total_q_count = len(pyqs)
    
    for t in topics:
        t_pyqs = [p for p in pyqs if p.topic_id == t.id]
        if not t_pyqs:
            continue
        q_count = len(t_pyqs)
        rep_count = sum([p.frequency_count for p in t_pyqs])
        percentage = (q_count / max(1, total_q_count)) * 100.0
        
        topic_items.append(TopicFrequencyItem(
            topic_name=t.name,
            question_count=q_count,
            repeated_count=rep_count,
            percentage=round(percentage, 2)
        ))
        
    # Sort topics by frequency percentage descending
    topic_items.sort(key=lambda x: x.percentage, reverse=True)
    
    # Find highly repeated questions (frequency > 2)
    repeated_qs = [p for p in pyqs if p.frequency_count >= 2]
    repeated_qs.sort(key=lambda x: x.frequency_count, reverse=True)
    
    return PYQAnalysisResponse(
        subject_id=subject_id,
        subject_name=subject.name,
        total_pyqs=len(pyqs),
        difficulty_distribution=difficulty_dist,
        important_topics=topic_items,
        repeated_questions=[PYQResponse.from_orm(p) for p in repeated_qs]
    )

@router.post("/notes/generate", response_model=NoteResponse)
def generate_study_notes(
    request: NoteGenerateRequest,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student)
):
    """
    Generate or retrieve study notes for a specific topic and note type.
    Supports dynamic custom topic names.
    """
    if request.topic_id:
        topic_id = request.topic_id
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        topic_name = topic.name
    elif request.custom_topic_name and request.subject_id:
        # Resolve or dynamically insert custom topic
        existing_topic = db.query(Topic).filter(
            Topic.subject_id == request.subject_id,
            Topic.name == request.custom_topic_name
        ).first()
        if existing_topic:
            topic = existing_topic
        else:
            topic = Topic(
                subject_id=request.subject_id,
                name=request.custom_topic_name,
                description="Custom topic added via AI notes generator"
            )
            db.add(topic)
            db.commit()
            db.refresh(topic)
        topic_id = topic.id
        topic_name = topic.name
    else:
        raise HTTPException(
            status_code=400, 
            detail="Either topic_id, or custom_topic_name + subject_id must be provided"
        )

    # Check if notes are already cached in database for this student & topic ID
    existing_note = db.query(GeneratedNote).filter(
        GeneratedNote.student_id == current_student.id,
        GeneratedNote.topic_id == topic_id,
        GeneratedNote.note_type == request.note_type
    ).first()
    
    if existing_note:
        return existing_note
        
    content = AIService.generate_notes(topic_name, request.note_type)
    
    note = GeneratedNote(
        student_id=current_student.id,
        topic_id=topic_id,
        note_type=request.note_type,
        content_markdown=content
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.post("/visual-notes/generate", response_model=VisualNoteResponse)
def generate_visual_notes(
    request: VisualNoteGenerateRequest,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student)
):
    """
    Generate structural data for visual summaries (mindmaps, flowcharts).
    """
    existing_visual = db.query(VisualNote).filter(
        VisualNote.student_id == current_student.id,
        VisualNote.topic_id == request.topic_id,
        VisualNote.visual_type == request.visual_type
    ).first()
    
    if existing_visual:
        return existing_visual
        
    topic = db.query(Topic).filter(Topic.id == request.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    structured_json = AIService.generate_visual_notes(topic.name, request.visual_type)
    
    visual = VisualNote(
        student_id=current_student.id,
        topic_id=request.topic_id,
        visual_type=request.visual_type,
        structured_json=structured_json
    )
    db.add(visual)
    db.commit()
    db.refresh(visual)
    return visual

@router.post("/planner/generate", response_model=List[StudyPlanResponse])
def generate_planner(
    request: PlannerGenerateRequest,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student)
):
    """
    Generate study plans based on topic listings and target exam date.
    Clears previous items for the subject first.
    """
    subject = db.query(Subject).filter(Subject.id == request.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
        
    topics = db.query(Topic).filter(Topic.subject_id == request.subject_id).all()
    if not topics:
        # No topics seeded for this subject — return empty schedule gracefully
        return []
        
    # Clear existing study plans for this student and subject
    db.query(StudyPlan).filter(
        StudyPlan.student_id == current_student.id,
        StudyPlan.subject_id == request.subject_id
    ).delete()
    
    generated_plans = AIService.generate_study_plan(
        student_id=current_student.id,
        subject_name=subject.name,
        exam_date=request.exam_date,
        daily_hours=request.daily_study_hours,
        topics=topics
    )
    
    db_plans = []
    for plan in generated_plans:
        db_plan = StudyPlan(
            student_id=plan["student_id"],
            subject_id=request.subject_id,
            topic_id=plan["topic_id"],
            scheduled_date=plan["scheduled_date"],
            duration_minutes=plan["duration_minutes"],
            status=plan["status"]
        )
        db.add(db_plan)
        db_plans.append(db_plan)
        
    db.commit()
    
    # Retrieve complete response with subject/topic text names resolved
    return get_schedule(db=db, current_student=current_student)

@router.get("/planner/schedule", response_model=List[StudyPlanResponse])
def get_schedule(
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student)
):
    """
    Get the complete active study schedule calendar list for the current student.
    """
    plans = db.query(StudyPlan).filter(StudyPlan.student_id == current_student.id).order_by(StudyPlan.scheduled_date).all()
    
    response = []
    for plan in plans:
        response.append(StudyPlanResponse(
            id=plan.id,
            subject_id=plan.subject_id,
            subject_name=plan.subject.name,
            topic_id=plan.topic_id,
            topic_name=plan.topic.name,
            scheduled_date=plan.scheduled_date,
            duration_minutes=plan.duration_minutes,
            status=plan.status
        ))
    return response

@router.put("/planner/schedule/{plan_id}", response_model=StudyPlanResponse)
def update_schedule_item(
    plan_id: int,
    status_update: StudyPlanUpdate,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student)
):
    """
    Update status of a scheduled planner event (Completed, Pending, Missed).
    """
    plan = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.student_id == current_student.id
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Schedule plan item not found")
        
    plan.status = status_update.status
    db.add(plan)
    db.commit()
    db.refresh(plan)
    
    return StudyPlanResponse(
        id=plan.id,
        subject_id=plan.subject_id,
        subject_name=plan.subject.name,
        topic_id=plan.topic_id,
        topic_name=plan.topic.name,
        scheduled_date=plan.scheduled_date,
        duration_minutes=plan.duration_minutes,
        status=plan.status
    )
