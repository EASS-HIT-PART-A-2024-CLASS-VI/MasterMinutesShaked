from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import asyncio
from datetime import datetime, timedelta

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    start_time = Column(String)
    end_time = Column(String)
    # duration_minutes = Column(Integer)
    priority = Column(String)
    notes = Column(String, nullable=True)
    date = Column(Date)

from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
print(DATABASE_URL)
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
    task_name: str
    start_time: str
    end_time: str
    priority: str
    day: str
    date: str
    notes: Optional[str] = None

class OutputSchema(BaseModel):
    schedule_id: str
    schedule: List[ScheduleItem]
    notes: Optional[str] = None

    