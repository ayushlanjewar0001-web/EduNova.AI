from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models import Student, University, Branch, Course, College
from app.schemas import StudentCreate, StudentResponse, StudentUpdate, Token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def get_current_student(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> Student:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    student = db.query(Student).filter(Student.email == email).first()
    if student is None:
        raise credentials_exception
    return student

@router.post("/register", response_model=StudentResponse)
def register(student_in: StudentCreate, db: Session = Depends(get_db)) -> Any:
    """
    Register a new student.
    """
    db_student = db.query(Student).filter(Student.email == student_in.email).first()
    if db_student:
        raise HTTPException(
            status_code=400,
            detail="A student with this email already exists in the system.",
        )
    hashed_password = get_password_hash(student_in.password)
    student = Student(
        email=student_in.email,
        password_hash=hashed_password,
        full_name=student_in.full_name,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@router.post("/token", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, retrieve a JWT access token.
    """
    student = db.query(Student).filter(Student.email == form_data.username).first()
    if not student or not verify_password(form_data.password, student.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            student.email, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.get("/me", response_model=StudentResponse)
def read_student_me(current_student: Student = Depends(get_current_student)) -> Any:
    """
    Get current active student details.
    """
    return current_student

@router.put("/profile", response_model=StudentResponse)
def update_student_profile(
    student_update: StudentUpdate,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
) -> Any:
    """
    Update student profile and Maharashtra academic context.
    """
    update_data = student_update.dict(exclude_unset=True)
    
    # Optional validations for IDs
    if "university_id" in update_data and update_data["university_id"]:
        univ = db.query(University).filter(University.id == update_data["university_id"]).first()
        if not univ:
            raise HTTPException(status_code=404, detail="University not found")
            
    for field, value in update_data.items():
        setattr(current_student, field, value)
        
    db.add(current_student)
    db.commit()
    db.refresh(current_student)
    return current_student
