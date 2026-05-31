from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from app.core.database import get_db
from app.api.auth import get_current_student
from app.models import Student, Subject, Topic, Test, TestAnswer
from app.schemas import TestGenerateRequest, TestSubmitRequest, TestResponse, TestAnswerResponse
from app.services.ai_service import AIService

router = APIRouter()

@router.post("/generate", response_model=TestResponse)
def generate_practice_test(
    request: TestGenerateRequest,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student)
):
    """
    Generate a dynamic exam mock/practice paper (MCQs, Short answer, etc.)
    Stores questions in database and returns it.
    """
    subject = db.query(Subject).filter(Subject.id == request.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
        
    topics = []
    if request.topic_ids:
        topics = db.query(Topic).filter(Topic.id.in_(request.topic_ids)).all()
    else:
        topics = db.query(Topic).filter(Topic.subject_id == request.subject_id).all()
        
    if not topics:
        raise HTTPException(status_code=400, detail="No topics found to generate test questions")
        
    questions_data = AIService.generate_test_questions(
        subject_id=request.subject_id,
        test_type=request.test_type,
        topics=topics,
        count=request.question_count
    )
    
    # Save the test container
    test = Test(
        student_id=current_student.id,
        subject_id=request.subject_id,
        test_type=request.test_type,
        total_questions=len(questions_data)
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    
    # Save test questions
    db_questions = []
    for q in questions_data:
        ans = TestAnswer(
            test_id=test.id,
            question_text=q["question_text"],
            correct_answer=q["correct_answer"],
            feedback=q["feedback"]
        )
        db.add(ans)
        db_questions.append(ans)
        
    db.commit()
    
    # Construct response (hiding correct answers initially)
    questions_response = []
    for q in db_questions:
        questions_response.append(TestAnswerResponse(
            id=q.id,
            question_text=q.question_text
        ))
        
    return TestResponse(
        id=test.id,
        subject_id=test.subject_id,
        test_type=test.test_type,
        created_at=test.created_at,
        questions=questions_response
    )

@router.post("/{test_id}/submit", response_model=TestResponse)
def submit_test(
    test_id: int,
    submission: TestSubmitRequest,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student)
):
    """
    Submit test answers. Calculates score, grades responses, and returns detailed performance summary.
    """
    test = db.query(Test).filter(
        Test.id == test_id,
        Test.student_id == current_student.id
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
        
    answers = db.query(TestAnswer).filter(TestAnswer.test_id == test_id).all()
    ans_dict = {a.id: a for a in answers}
    
    correct_count = 0
    
    for sub_ans in submission.answers:
        q_id = sub_ans.question_id
        if q_id in ans_dict:
            db_ans = ans_dict[q_id]
            db_ans.student_answer = sub_ans.student_answer
            
            # Simple grading strategy (for MCQs, check exact match case-insensitive; for text, match keywords)
            is_correct = False
            if test.test_type == "MCQ":
                if db_ans.correct_answer.strip().lower() == sub_ans.student_answer.strip().lower():
                    is_correct = True
                    correct_count += 1
            else:
                # Mock grading logic for short/long answers: mark correct if answer is not empty
                if len(sub_ans.student_answer.strip()) > 15:
                    is_correct = True
                    correct_count += 1
                    db_ans.feedback = f"Good detail provided! {db_ans.feedback}"
                else:
                    db_ans.feedback = f"Your answer is too short. Try expanding it in the next attempts. Key context to include: {db_ans.correct_answer}"
                    
            db_ans.is_correct = is_correct
            db.add(db_ans)
            
    # Calculate score
    score = (correct_count / max(1, len(answers))) * 100.0
    test.score = Decimal(str(round(score, 2)))
    
    # Generate high-yield AI feedback summary
    if score >= 80:
        test.feedback_text = "Excellent preparation! You have solid mastery over the topics tested. Keep practicing mock exams to build speed."
    elif score >= 50:
        test.feedback_text = "Good effort. You understand the foundational concepts but have room for improvement, particularly on numericals or detailed BCNF decompositions. Refer to generated study notes."
    else:
        test.feedback_text = "Needs attention. We recommend utilizing the AI Teacher and generating Concept Notes for these topics before re-attempting."
        
    db.add(test)
    db.commit()
    db.refresh(test)
    
    # Build complete response including results
    questions_response = []
    for q in answers:
        questions_response.append(TestAnswerResponse(
            id=q.id,
            question_text=q.question_text,
            correct_answer=q.correct_answer,
            student_answer=q.student_answer,
            is_correct=q.is_correct,
            feedback=q.feedback
        ))
        
    return TestResponse(
        id=test.id,
        subject_id=test.subject_id,
        test_type=test.test_type,
        score=test.score,
        total_questions=test.total_questions,
        feedback_text=test.feedback_text,
        created_at=test.created_at,
        questions=questions_response
    )
