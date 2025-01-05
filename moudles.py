from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

class Task(BaseModel):
    name: str
    duration_minutes: int
    priority: str
    notes: Optional[str] = None
class Break(BaseModel):
    start: str
    end: str
class InputSchema(BaseModel):
    tasks: List[Task]
    constraints: dict
    working_days: Optional[List[str]] = None  # Defaults to None if not provided


class ScheduleItem(BaseModel):
    task_id: str
    task_name: str
    start_time: str
    end_time: str
    priority: str
    notes: Optional[str] = None

class OutputSchema(BaseModel):
    schedule_id: str
    schedule: List[ScheduleItem]
    notes: Optional[str] = None