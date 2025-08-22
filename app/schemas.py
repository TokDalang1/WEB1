from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field

from .models import UserRole, AttendanceStatus


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: UserRole

    class Config:
        from_attributes = True


class ClassCreate(BaseModel):
    name: str


class ClassOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class StudentCreate(BaseModel):
    student_code: str
    name: str
    class_id: Optional[int] = None
    username: str
    password: str


class StudentOut(BaseModel):
    id: int
    student_code: str
    name: str
    class_id: Optional[int]
    user: UserOut

    class Config:
        from_attributes = True


class TeacherCreate(BaseModel):
    teacher_code: str
    name: str
    username: str
    password: str


class TeacherOut(BaseModel):
    id: int
    teacher_code: str
    name: str
    user: UserOut

    class Config:
        from_attributes = True


class AttendanceCreate(BaseModel):
    image_base64: Optional[str] = Field(None, description="Base64 image data; YOLO stub ignores content")
    note: Optional[str] = None


class AttendanceUpdate(BaseModel):
    status: AttendanceStatus
    note: Optional[str] = None


class AttendanceOut(BaseModel):
    id: int
    student_id: int
    date: date
    status: AttendanceStatus
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True