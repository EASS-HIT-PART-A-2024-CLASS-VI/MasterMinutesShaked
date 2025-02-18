from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import json
import os
import uuid
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv
import uvicorn
import redis

from moudles import InputSchema, OutputSchema, ScheduleItem, Task, SessionLocal

app = FastAPI()

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")

if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-1.5-flash-002"

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

redis_client = redis.Redis.from_url(REDIS_URL)

# Helper function to cache data in Redis
def cache_data(key: str, data: dict, expiration: int = 3600):
    redis_client.setex(key, expiration, json.dumps(data))

# Helper function to get data from Redis cache
def get_cached_data(key: str) -> Optional[dict]:
    cached_data = redis_client.get(key)
    if cached_data:
        return json.loads(cached_data)
    return None

# POST endpoint to generate a schedule with Gemini handling task scheduling
@app.post("/schedule", response_model=OutputSchema)
async def generate_schedule(input_data: InputSchema, db: Session = Depends(get_db)):
    try:
        # Update the prompt to explicitly request JSON format
        gemini_input = {
            "messages": [
                {"role": "user", "parts": [{"text": f"Please create a task schedule that starting today based on the following input: {json.dumps(input_data.dict())}"}]},
            ],
            "model": MODEL_NAME,
            "temperature": 0.1
        }
        print(gemini_input)

        # Call Gemini API to generate the schedule
        gemini_response = await query_gemini_model(request=gemini_input)
        
        # Log the raw response for debugging
        print("Gemini Response (Raw):", gemini_response)

        response_text = gemini_response.get("response_text", None)

        if response_text:
            # Clean the response to remove any code block markdown
            cleaned_response_text = response_text.strip("```json").replace("```", "").strip()
            print(cleaned_response_text)
            try:
                # Try to parse the cleaned response as JSON
                schedule_data = json.loads(cleaned_response_text)
                schedule_data = {"schedule": schedule_data}
                print("Parsed Gemini Schedule:", schedule_data)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail=f"Failed to parse Gemini's response into valid JSON. Raw response: {cleaned_response_text}")

            # Ensure that the returned schedule is valid
            if "schedule" not in schedule_data:
                raise HTTPException(status_code=400, detail="Gemini's response does not contain a valid schedule.")

            # Save the generated schedule to the database
            schedule_id = str(uuid.uuid4())
            print(schedule_data)
            for task in schedule_data["schedule"]:
                db_task = Task(
                    id=task["task_id"],
                    name=task["task_name"],
                    start_time = task["start_time"],
                    end_time = task["end_time"],
                    # duration_minutes=task["duration_minutes"],
                    priority=task["priority"],
                    notes=task.get("notes"),
                    date=datetime.strptime(task["date"], "%Y-%m-%d").date()
                )
                db.add(db_task)
            db.commit()
            cache_data(schedule_id, schedule_data)

            return OutputSchema(schedule_id=schedule_id, schedule=schedule_data["schedule"], notes=schedule_data.get("notes", ""))

        else:
            raise HTTPException(status_code=400, detail="No response text received from Gemini.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheduling failed: {str(e)}")

# PUT endpoint to update a task in the schedule
@app.put("/schedule/{schedule_id}/task/{task_id}")
async def update_task(schedule_id: str, task_id: str, updated_task: ScheduleItem, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.name = updated_task.task_name
    task.start_time = datetime.strptime(updated_task.start_time, "%H:%M").time()
    task.end_time = datetime.strptime(updated_task.end_time, "%H:%M").time()
    task.priority = updated_task.priority
    task.notes = updated_task.notes
    db.commit()

    return {"message": "Task updated", "updated_task": updated_task}

# GET endpoint to fetch the schedule by ID
@app.get("/schedule/{schedule_id}", response_model=OutputSchema)
async def get_schedule(schedule_id: str, db: Session = Depends(get_db)):
    cached_schedule = get_cached_data(schedule_id)
    if cached_schedule:
        return OutputSchema(schedule_id=schedule_id, schedule=cached_schedule["schedule"], notes=cached_schedule.get("notes"))

    tasks = db.query(Task).filter(Task.schedule_id == schedule_id).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="Schedule not found")

    schedule = [ScheduleItem(
        task_id=task.id,
        task_name=task.name,
        start_time=task.start_time.strftime("%H:%M"),
        end_time=task.end_time.strftime("%H:%M"),
        priority=task.priority,
        day=task.date.strftime("%A"),
        date=task.date.strftime("%Y-%m-%d"),
        notes=task.notes
    ) for task in tasks]

    cache_data(schedule_id, {"schedule": schedule})

    return OutputSchema(schedule_id=schedule_id, schedule=schedule, notes=None)

# Function to query Gemini model
@app.post("/gemini/query")
async def query_gemini_model(request: Dict[str, Any]) -> Dict[str, Any]:
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds
    today = date.today()
    current_hour = datetime.now().time()
    system_instruction = f"""You are a meticulous task scheduler that generates schedules in JSON format. Given a set of tasks (name, duration in minutes, priority and optional notes) and constraints (duration, priority - High > Medium > Low, working hours, and available days), create an optimal schedule that respects working hours, breaks, and task priorities.

                Output a valid JSON array of tasks. Each task object must include the following fields:

                *   `task_id`: A valid UUID (version 4).
                *   `task_name`: The name of the task.
                *   `start_time`: The task's start time (in HH:MM 24-hour format)
                *   `end_time`: The task's end time (in HH:MM 24-hour format).
                *   `priority`: The task's priority (High, Medium, or Low).
                *   `day`: The day of the week (e.g., Monday, Tuesday, etc.).
                *   `date`: The full date (YYYY-MM-DD) starting from next week ,today (today is {today.strftime("%Y-%m-%d")}) . 
                *   `notes`: (Optional) Any relevant notes about the task.

                Include breaks as tasks with `priority: "High"` and a descriptive `task_name` (e.g., "Lunch Break", "Short Break").

                Schedule only the provided tasks; do not add filler tasks. It's acceptable to have unscheduled time within the working day.

                If all tasks cannot be scheduled in a single day, schedule remaining tasks on subsequent working days . Do not schedule tasks on non-working days

                If a task's duration exceeds any contiguous block of time available in a given day, just schedule it in the next day. Every task must be scheduled EXACTLY ONCE!
                The task that appeared next day should be limit by working_hours and workdays and breaks and priority.

                starting date of the task should be next week (today is {today.strftime("%Y-%m-%d")}). 
                Assume the input will include the following information:

                *   `working_hours`: Start and end times of the working day (e.g., "09:00-17:00").
                *   `workdays`: An array of working days (e.g., ["Sunday","Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]).
                *   `tasks`: An array of task objects, each with `task_name`, `duration` (in hours), and `priority`.

                Prioritize completing higher-priority tasks first. In case of scheduling conflicts, prioritize higher-priority tasks.

                Return only the JSON schedule. Do not include any explanatory text or commentary."""
    model = genai.GenerativeModel(request["model"], system_instruction=system_instruction)

    for attempt in range(MAX_RETRIES):
        try:
            messages = [{'role': 'user', 'parts': [{'text': message['parts'][0]['text']}]} for message in request["messages"]]

            response = model.generate_content(messages, generation_config={"temperature": request["temperature"]})

            if response.text:
                return {"response_text": response.text}
            else:
                print("Failed to process the model response.")
                return {}

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
            else:
                raise HTTPException(status_code=500, detail=f"Failed to query Gemini API: {str(e)}")

    raise HTTPException(status_code=500, detail="Failed to query Gemini API after multiple retries")

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    try:
        # Check if port is in use
        import socket
        s = socket.socket()
        try:
            s.bind(("127.0.0.1", 1236))
        finally:
            s.close()
        
        uvicorn.run(app, host="127.0.0.1", port=1236)
    except Exception as e:
        print(f"Server startup failed: {e}")
        exit(1)