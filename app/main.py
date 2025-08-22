from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .database import Base, engine, SessionLocal
from .auth import hash_password
from .models import User, UserRole
from .routers import users as users_router
from .routers import admin as admin_router
from .routers import attendance as attendance_router

app = FastAPI(title="Presensi SMP - YOLO Face Recognition (Stub)")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# Create DB tables
Base.metadata.create_all(bind=engine)


# Seed admin user if not exists
@app.on_event("startup")
def seed_admin():
    db: Session = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            admin = User(
                username="admin",
                full_name="Administrator",
                password_hash=hash_password("admin123"),
                role=UserRole.admin,
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


# Wire routers
app.include_router(users_router.router)
app.include_router(admin_router.router)
app.include_router(attendance_router.router)


@app.get("/")
def root():
    return FileResponse("static/index.html")