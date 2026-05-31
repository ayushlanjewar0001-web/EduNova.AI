from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models import University, College, Course, Branch, Subject, Topic
from app.schemas import (
    UniversityResponse, CollegeResponse, CourseResponse, 
    BranchResponse, SubjectResponse, TopicResponse
)

router = APIRouter()

@router.get("/universities", response_model=List[UniversityResponse])
def get_universities(db: Session = Depends(get_db)):
    """
    List all supported universities in Maharashtra.
    """
    return db.query(University).all()

@router.get("/universities/{id}/colleges", response_model=List[CollegeResponse])
def get_colleges(id: int, db: Session = Depends(get_db)):
    """
    List colleges associated with a university.
    """
    return db.query(College).filter(College.university_id == id).all()

@router.get("/courses", response_model=List[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    """
    List all available courses.
    """
    return db.query(Course).all()

@router.get("/branches", response_model=List[BranchResponse])
def get_branches(course_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    List branches, optionally filtered by course_id.
    """
    query = db.query(Branch)
    if course_id:
        query = query.filter(Branch.course_id == course_id)
    return query.all()

@router.get("/subjects", response_model=List[SubjectResponse])
def get_subjects(
    university_id: Optional[int] = Query(None, description="Filter subjects by university ID"),
    branch_id: int = Query(..., description="Filter subjects by branch ID"),
    semester: int = Query(..., description="Filter subjects by semester"),
    db: Session = Depends(get_db)
):
    """
    List subjects for a specific university, branch, and semester (Curriculum Resolver).
    """
    query = db.query(Subject).filter(
        Subject.branch_id == branch_id,
        Subject.semester == semester
    )
    if university_id:
        query = query.filter(Subject.university_id == university_id)
    return query.all()

@router.get("/topics/{subject_id}", response_model=List[TopicResponse])
def get_topics(subject_id: int, db: Session = Depends(get_db)):
    """
    List all topics for a specific subject.
    """
    return db.query(Topic).filter(Topic.subject_id == subject_id).all()
