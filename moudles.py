from pydantic import BaseModel
from typing import List, Optional

# Input schema
class Task(BaseModel):
    id: str
    name: str
    priority: str  # "high", "medium", or "low"
    duration_minutes: int
    deadline: Optional[str]  # ISO format: "YYYY-MM-DDTHH:MM:SSZ"

class Break(BaseModel):
    start: str  # "HH:MM"
    end: str  # "HH:MM"

class Constraints(BaseModel):
    work_hours_start: str  # "HH:MM"
    work_hours_end: str  # "HH:MM"
    breaks: List[Break]

class InputSchema(BaseModel):
    tasks: List[Task]
    constraints: Constraints

# Output schema
class ScheduleItem(BaseModel):
    task_id: str
    start_time: str  # "HH:MM"
    end_time: str  # "HH:MM"

class OutputSchema(BaseModel):
    schedule: List[ScheduleItem]
    notes: str

# 3. Example input
input_data = {
    "tasks": [
        {"id": "1", "name": "Write report", "priority": "high", "duration_minutes": 120, "deadline": "2024-12-17T12:00:00Z"},
        {"id": "2", "name": "Team meeting", "priority": "medium", "duration_minutes": 60, "deadline": None}
    ],
    "constraints": {
        "work_hours_start": "09:00",
        "work_hours_end": "17:00",
        "breaks": [{"start": "12:00", "end": "13:00"}]
    }
}

# Validate input
validated_input = InputSchema(**input_data)
print("Validated Input:", validated_input.model_dump_json(indent=2))

# 4. Example LLM response
response_data = {
    "schedule": [
        {"task_id": "1", "start_time": "09:00", "end_time": "11:00"},
        {"task_id": "2", "start_time": "13:00", "end_time": "14:00"}
    ],
    "notes": "High-priority tasks scheduled first. Break added from 12:00 to 13:00."
}

# Validate response
validated_response = OutputSchema(**response_data)
print("Validated Response:", validated_input.model_dump_json(indent=2))