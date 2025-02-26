from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, Date, Boolean, DateTime, func, create_engine, UUID, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(String, primary_key=True, index=True)
    schedule_id = Column(String, ForeignKey("schedule.id"))
    # user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, index=True)
    start_time = Column(String)
    end_time = Column(String)
    # duration_minutes = Column(Integer)
    priority = Column(String)
    notes = Column(String, nullable=True)
    date = Column(Date)

class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    # task_id = Column(String, ForeignKey("tasks.id"), nullable=False)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
# print(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Pydantic models for request and response validation
class TaskSchema(BaseModel):
    name: str
    duration_minutes: int
    priority: str
    notes: Optional[str] = None

class Break(BaseModel):
    start: str
    end: str

class InputSchema(BaseModel):
    tasks: List[TaskSchema]
    constraints: dict
    working_days: Optional[List[str]] = None  # Defaults to None if not provided
    start_hour_day: str  # Start day of the schedule
    end_hour_day: str  # End day of the schedule
    Breaks: Optional[List[Break]] = None

class ScheduleItem(BaseModel):
    task_id: str
    # user_id: str  # Link task to a specific user
    task_name: str
    start_time: str  # Assuming "HH:MM" format
    end_time: str
    priority: str  # e.g., "High", "Medium", "Low"
    day: str  # e.g., "Monday"
    date: str  # "YYYY-MM-DD"
    notes: Optional[str] = None

class OutputSchema(BaseModel):
    schedule_id: str
    schedule: List[ScheduleItem]
    notes: Optional[str] = None

from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: str
    is_active: bool

class Config:
    orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None