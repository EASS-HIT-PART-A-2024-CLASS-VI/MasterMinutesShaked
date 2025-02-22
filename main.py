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
from telegram import Bot
from fastapi.security import OAuth2PasswordRequestForm
from auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_active_user

from moudles import InputSchema, OutputSchema, ScheduleItem, Task, SessionLocal

app = FastAPI()

# Load environment variables from .env file
load_dotenv()

# Get API keys and URLs from environment variables
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
print(DATABASE_URL, GEMINI_API_KEY, REDIS_URL)

if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")



genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-1.5-pro-002"

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

# Helper function to send schedule to Telegram
def send_schedule_to_telegram(schedule: dict):
    message = "Here is your schedule:\n\n"
    for task in schedule["schedule"]:
        message += f"Task: {task['task_name']}\n"
        message += f"Start Time: {task['start_time']}\n"
        message += f"End Time: {task['end_time']}\n"
        message += f"Priority: {task['priority']}\n"
        message += f"Date: {task['date']}\n"
        message += f"Notes: {task.get('notes', 'None')}\n\n"
    Bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

# POST endpoint to generate a schedule with Gemini handling task scheduling
@app.post("/schedule", response_model=OutputSchema)
async def generate_schedule(input_data: InputSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)):
   
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
                    id=str(uuid.uuid4()),  # Generate a unique UUID for each task
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
            send_schedule_to_telegram(schedule_data)

            return OutputSchema(schedule_id=schedule_id, schedule=schedule_data["schedule"], notes=schedule_data.get("notes", ""))

        else:
            raise HTTPException(status_code=400, detail="No response text received from Gemini.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheduling failed: {str(e)}")

# PUT endpoint to update a task in the schedule
@app.put("/schedule/{schedule_id}/task/{task_id}")
async def update_task(schedule_id: str, task_id: str, updated_task: ScheduleItem, db: Session = Depends(get_db),
                      current_user=Depends(get_current_active_user)):
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
async def get_schedule(schedule_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
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
    system_instruction = f"""You are a task scheduler that generates JSON schedules using the Pomodoro technique.
Given a list of tasks (`task_name`, `duration` in minutes, `priority`, and optional `notes`) and constraints 
(`working_hours`, `workdays`), create an optimized schedule that:

- **Breaks all tasks into 25-minute Pomodoro sessions**, inserting **a 5–10 minute break after each**.
- **Ensures all task time is fully scheduled** without exceeding the total duration.
- **Handles remaining minutes correctly**:
  - If a task’s duration **is a multiple of 25**, schedule Pomodoro sessions normally.
  - If a task’s duration **is not a multiple of 25**, schedule full 25-minute Pomodoro sessions first, then schedule the remaining time as a final shorter session.
- **No consecutive 25-minute sessions without a break**—every Pomodoro session must be followed by a short break.
- **Schedules the next available task as soon as possible** within working hours (no unnecessary gaps).
- **Prioritizes tasks (High > Medium > Low)** and efficiently fills available time.
- Moves sessions to the next available workday if no contiguous time block is available.
- Includes breaks as tasks with `priority: "High"` (e.g., "Short Break", "Lunch Break").
- Starts scheduling from **next week** (today is {today.strftime("%Y-%m-%d")}).

### **Output Format**
Output a JSON array of scheduled Pomodoro sessions and breaks. Each session is a separate task object containing:
- `task_id`: UUID v4
- `task_name`: Task name
- `start_time`, `end_time`: HH:MM format (24-hour)
- `priority`: High, Medium, or Low
- `day`: Day of the week
- `date`: YYYY-MM-DD
- `notes`: (Optional) Task notes

### **Task Splitting Formula**
For a task with `X` total minutes:
1. **Divide X by 25** → This gives the number of full Pomodoro sessions (`N`).
2. **The remainder R = X - (N × 25)**:
   - If `R = 0`, schedule `N` full Pomodoro sessions.
   - If `R > 0`, schedule `N` full Pomodoro sessions + **one final session of R minutes**.
3. **Every 25-minute session must be followed by a short break (5–10 minutes).**
4. **Ensure all scheduled time exactly matches X—do not exceed or lose minutes.**

### **Examples**
#### **Example 1: "Team Meeting" (90 minutes)**
90 ÷ 25 = 3 full sessions, remainder 15 → Schedule as:
- **Session 1:** 25 minutes (09:00–09:25)
- **Short Break:** 5 minutes (09:25–09:30)
- **Session 2:** 25 minutes (09:30–09:55)
- **Short Break:** 5 minutes (09:55–10:00)
- **Session 3:** 25 minutes (10:00–10:25)
- **Short Break:** 5 minutes (10:25–10:30)
- **Final Session:** 15 minutes (10:30–10:45)

#### **Example 2: "Weekly Sync" (60 minutes)**
60 ÷ 25 = 2 full sessions, remainder 10 → Schedule as:
- **Session 1:** 25 minutes (10:45–11:10)
- **Short Break:** 5 minutes (11:10–11:15)
- **Session 2:** 25 minutes (11:15–11:40)
- **Short Break:** 5 minutes (11:40–11:45)
- **Final Session:** 10 minutes (11:45–11:55)

#### **Example 3: "Code Review" (45 minutes)**
45 ÷ 25 = 1 full session, remainder 20 → Schedule as:
- **Session 1:** 25 minutes (11:55–12:20)
- **Short Break:** 5 minutes (12:20–12:25)
- **Final Session:** 20 minutes (12:25–12:45)

#### **Example 4: "Deep Work" (120 minutes)**
120 ÷ 25 = 4 full sessions, remainder 0 → Schedule as:
- **Session 1:** 25 minutes (13:00–13:25)
- **Short Break:** 5 minutes (13:25–13:30)
- **Session 2:** 25 minutes (13:30–13:55)
- **Short Break:** 5 minutes (13:55–14:00)
- **Session 3:** 25 minutes (14:00–14:25)
- **Short Break:** 5 minutes (14:25–14:30)
- **Session 4:** 25 minutes (14:30–14:55)
- **Short Break:** 5 minutes (14:55–15:00)

> ⚠ **Do not schedule an extra 25-minute session if only 10, 15, or 20 minutes remain. Use the exact remaining time as the final session.**

### **Additional Constraints**
- **No unnecessary gaps**—schedule the next available task immediately if time allows.
- **Higher-priority tasks take precedence** in case of conflicts.
- **Return only the JSON schedule—no explanations or extra text.**
"""



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

@app.on_event("startup")
async def start_notification_service():
    # This creates a background asyncio task that will run alongside your FastAPI endpoints.
    asyncio.create_task(notification_loop())

async def notification_loop():
    """Periodically check for tasks starting in 10 minutes and send notifications."""
    while True:
        await check_and_send_notifications()
        await asyncio.sleep(60)  # Wait 60 seconds before checking again

async def check_and_send_notifications():
    """Check the database for tasks that are scheduled to start in 10 minutes and send a Telegram reminder."""
    session = SessionLocal()
    try:
        now = datetime.now()
        # Calculate the target time (10 minutes from now)
        # target_time = now + timedelta(minutes=10)
        # We create a window [target_time, target_time + 1 minute) to catch tasks scheduled at that minute.
        lower_bound = now.replace(second=0, microsecond=0)
        upper_bound = lower_bound + timedelta(minutes=11)

        # Query all tasks (in a more advanced version, filter by date and notified status)
        tasks = session.query(Task).all()
        if not tasks:
            print("no tasks found")
            return  # No tasks found

        # Initialize the Telegram Bot
        bot = Bot(token=TELEGRAM_TOKEN)

        for task in tasks:
            try:
                # Combine the task's date and start_time string (assumed to be in "HH:MM" format)
                task_time = datetime.combine(task.date, datetime.strptime(task.start_time, "%H:%M").time())
                # Check if the task's scheduled datetime falls within our target window.
                if lower_bound <= task_time < upper_bound:
                    message = (
                        f"Reminder: Your task '{task.name}' is scheduled to start at "
                        f"{task.start_time} on {task.date.strftime('%Y-%m-%d')}."
                    )
                    print(message)
                    print(TELEGRAM_CHAT_ID)
                    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
                    print(f"Sent notification for task {task.id}")
                    # Optionally update the task (e.g., task.notified = True) to avoid sending duplicate notifications.
            except Exception as e:
                print(f"Error processing task {task.id}: {e}")
        session.commit()
    except Exception as e:
        print(f"Error in notification service: {e}")
    finally:
        session.close()

# @app.post("/token", response_model=Token)
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     # Authenticate the user using the fake users database.
#     user = authenticate_user(fake_users_db, form_data.username, form_data.password)
#     if not user:
#          raise HTTPException(status_code=400, detail="Incorrect username or password")
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#          data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}

from moudles import UserCreate, UserOut, Token
from moudles import User
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_db,
    get_current_active_user,
    get_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from fastapi.security import OAuth2PasswordRequestForm

@app.post("/register", response_model=UserOut)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user_create.username).first()
    if db_user:
         raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user_create.password)
    new_user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
         raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


import moudles as models
@app.get("/users/me", response_model=UserOut)
def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user

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