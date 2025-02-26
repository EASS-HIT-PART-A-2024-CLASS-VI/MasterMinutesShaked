from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import json
import asyncio
from dotenv import load_dotenv
import uvicorn
from telegram import Bot
from backend.db.moudles import Task, SessionLocal  # Make sure your moudles module exposes these
from backend.auth.auth import get_current_active_user  # Import your current active user dependency
import backend.db.moudles as models

# Load environment variables from .env file
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
print("telegram-token:"+TELEGRAM_TOKEN)
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/tasks_db")
app = FastAPI()

# Allow all origins for testing (adjust as needed)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to split and send long messages via Telegram
async def send_long_message(bot: Bot, chat_id: str, message: str):
    max_length = 4000  # Telegram's safe limit is 4096, so we use 4000 for a margin.
    parts = [message[i : i + max_length] for i in range(0, len(message), max_length)]
    for part in parts:
        await bot.send_message(chat_id=chat_id, text=part, parse_mode="Markdown")

@app.get("/get_schedule/{schedule_id}")
async def get_schedule_telegram(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)  # Ensure we get the authenticated user
):
    # Fetch tasks for the current user
    tasks = db.query(Task).filter(Task.schedule_id == schedule_id).all()
    if not tasks:
        return {"message": "No tasks found in the schedule for this user"}

    # Build the message to be sent to Telegram
    message = "📅 **Your Current Schedule:**\n\n"
    for task in tasks:
        task_info = (
            f"📌 **Task:** {task.name}\n"
            f"🕒 **Start:** {task.start_time}\n"
            f"🕘 **End:** {task.end_time}\n"
            f"🎯 **Priority:** {task.priority}\n"
            f"📅 **Date:** {task.date}\n"
            f"📝 **Notes:** {task.notes or 'None'}\n\n"
        )
        # If adding this task exceeds our message length limit, send current message and reset.
        if len(message) + len(task_info) > 4000:
            bot = Bot(token=TELEGRAM_TOKEN)
            await send_long_message(bot, TELEGRAM_CHAT_ID, message)
            message = "📅 **Continued Schedule:**\n\n"
        message += task_info

    # Send any remaining message content
    bot = Bot(token=TELEGRAM_TOKEN)
    await send_long_message(bot, TELEGRAM_CHAT_ID, message)

    return {"message": "Schedule sent to Telegram"}

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
        lower_bound = now + timedelta(minutes=10)
        upper_bound = lower_bound + timedelta(minutes=1)

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

if __name__ == "__main__":
    # Run the microservice on a different port (e.g., 8001) to keep it separate from other services.
    uvicorn.run(app, host="0.0.0.0", port=8001)