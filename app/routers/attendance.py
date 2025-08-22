from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..auth import get_db, require_role
from ..models import User, UserRole, Student, Attendance, AttendanceStatus
from .. import schemas

router = APIRouter(prefix="/attendance", tags=["attendance"]) 


@router.post("/checkin", response_model=schemas.AttendanceOut)
def checkin(
    payload: schemas.AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.student)),
):
    # YOLO stub: trust current logged-in student as recognized
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found")

    today = date.today()
    existing = db.query(Attendance).filter(Attendance.student_id == student.id, Attendance.date == today).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in today")

    record = Attendance(student_id=student.id, date=today, status=AttendanceStatus.present, note=payload.note)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/mine", response_model=list[schemas.AttendanceOut])
def my_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.student)),
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found")
    return db.query(Attendance).filter(Attendance.student_id == student.id).order_by(Attendance.date.desc()).all()


@router.get("/day", response_model=list[schemas.AttendanceOut], dependencies=[Depends(require_role(UserRole.teacher, UserRole.admin))])
def list_by_day(day: date = Query(default_factory=date.today), db: Session = Depends(get_db)):
    return db.query(Attendance).filter(Attendance.date == day).all()


@router.patch("/{attendance_id}", response_model=schemas.AttendanceOut, dependencies=[Depends(require_role(UserRole.teacher, UserRole.admin))])
def update_attendance(attendance_id: int, payload: schemas.AttendanceUpdate, db: Session = Depends(get_db)):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance not found")
    record.status = payload.status
    record.note = payload.note
    db.commit()
    db.refresh(record)
    return record