from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_db, require_role
from ..models import User, UserRole, Class, Student, Teacher
from .. import schemas
from ..auth import hash_password

router = APIRouter(prefix="/admin", tags=["admin"]) 


# Classes
@router.post("/classes", response_model=schemas.ClassOut, dependencies=[Depends(require_role(UserRole.admin))])
def create_class(payload: schemas.ClassCreate, db: Session = Depends(get_db)):
    existing = db.query(Class).filter(Class.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Class name already exists")
    obj = Class(name=payload.name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/classes", response_model=list[schemas.ClassOut], dependencies=[Depends(require_role(UserRole.admin))])
def list_classes(db: Session = Depends(get_db)):
    return db.query(Class).order_by(Class.name).all()


# Students
@router.post("/students", response_model=schemas.StudentOut, dependencies=[Depends(require_role(UserRole.admin))])
def create_student(payload: schemas.StudentCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(username=payload.username, full_name=payload.name, password_hash=hash_password(payload.password), role=UserRole.student)
    db.add(user)
    db.flush()

    student = Student(student_code=payload.student_code, name=payload.name, class_id=payload.class_id, user_id=user.id)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("/students", response_model=list[schemas.StudentOut], dependencies=[Depends(require_role(UserRole.admin))])
def list_students(db: Session = Depends(get_db)):
    return db.query(Student).all()


# Teachers
@router.post("/teachers", response_model=schemas.TeacherOut, dependencies=[Depends(require_role(UserRole.admin))])
def create_teacher(payload: schemas.TeacherCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(username=payload.username, full_name=payload.name, password_hash=hash_password(payload.password), role=UserRole.teacher)
    db.add(user)
    db.flush()

    teacher = Teacher(teacher_code=payload.teacher_code, name=payload.name, user_id=user.id)
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


@router.get("/teachers", response_model=list[schemas.TeacherOut], dependencies=[Depends(require_role(UserRole.admin))])
def list_teachers(db: Session = Depends(get_db)):
    return db.query(Teacher).all()