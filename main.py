from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import json
import os
from typing import Dict, Any
import uvicorn
import time
import datetime

from moudles import InputSchema, OutputSchema, ScheduleItem, Task
import uuid
import asyncio
import google.generativeai as genai
import os
from dotenv import load_dotenv
import genai

app = FastAPI()

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-1.5-pro-002"

# In-memory storage for GET endpoint
saved_schedule = {}

# POST endpoint to generate a schedule with Gemini handling task scheduling
@app.post("/schedule", response_model=OutputSchema)
async def generate_schedule(input_data: InputSchema):
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
        #print(gemini_input['messages'])
        # gemini_input = {
        #     "system_instruction":
        #     {
        #         "parts": [
        #             {"text":  """You are a meticulous task scheduler that generates schedules in JSON format. Given a set of tasks and constraints (duration, priority - High > Medium > Low, working hours, and available days), create an optimal schedule that respects working hours, breaks, and task priorities.

        #         Output a valid JSON array of tasks. Each task object must include the following fields:

        #         *   `task_id`: A valid UUID (version 4).
        #         *   `task_name`: The name of the task.
        #         *   `start_time`: The task's start time (in HH:MM 24-hour format).
        #         *   `end_time`: The task's end time (in HH:MM 24-hour format).
        #         *   `priority`: The task's priority (High, Medium, or Low).
        #         *   `day`: The day of the week (e.g., Monday, Tuesday, etc.).
        #         *   `date`: The full date (YYYY-MM-DD).
        #         *   `notes`: (Optional) Any relevant notes about the task.

        #         Include breaks as tasks with `priority: "High"` and a descriptive `task_name` (e.g., "Lunch Break", "Short Break").

        #         Schedule only the provided tasks; do not add filler tasks. It's acceptable to have unscheduled time within the working day.

        #         If all tasks cannot be scheduled in a single day, schedule remaining tasks on subsequent working days. Do not schedule tasks on non-working days.

        #         If a task's duration exceeds the remaining available time in a day, split the task into multiple entries. Each split must:

        #         *   Have the same `task_id`.
        #         *   Represent a contiguous block of time.
        #         *   Be scheduled on consecutive working days if necessary.

        #         If a task is split, you have to make sure that only the remainder time is scheduled (e.g., if a three hours task is split such that you complete two hours in one day, the next day should contain one hour exactly, as 3-2=1)

        #         Example of a split task: A 3-hour task with only 2 hours remaining in the day should be split into two entries: one 2-hour entry on the current day and one 1-hour entry on the next working day.

        #         Assume the input will include the following information:

        #         *   `working_hours`: Start and end times of the working day (e.g., "09:00-17:00").
        #         *   `workdays`: An array of working days (e.g., ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]).
        #         *   `tasks`: An array of task objects, each with `task_name`, `duration` (in hours), and `priority`.

        #         Prioritize completing higher-priority tasks first. In case of scheduling conflicts, prioritize higher-priority tasks.

        #         Return only the JSON schedule. Do not include any explanatory text or commentary."""
        #     }]
        #     },
        #     "messages": [
        #         # {"role": "system", "parts": [{"text": "You are a task scheduler that outputs schedules in JSON format. Given a set of tasks and constraints (duration of task, prioritization - high tasks are more important than medium tasks which are more important than low priority tasks, working hours during the workday), please create a schedule that respects working hours, breaks, and task priorities. Ensure the output is a valid JSON array of tasks, each with a task_id (should be a VALID uuid), task_name, start_time, end_time, priority, day (day of the week) and the date (the date of the day of the week), and an optional notes. You should put the break as part of the response (break's priority should be 'high'). You only need to schedule the tasks, do not fill my day with pointless tasks (you don't need to fill out the entire day, it's okay if I still have leftover time). If you cannot schedule all tasks in one day, move them to the next day (but only to valid working days, do not schedule on non-working days). If a task cannot be completed in a continuous manner (e.g., it is three hours long but you only have two hours left in a day), feel free to split it (you can split tasks across the day, and even split them between days - so if for example a task is two hours long but you only have one hour left in a day, schedule one hour in one day and the remaining in the next day - just make sure they have the same task id)"}]},
        #         {"role": "user", "parts": [{"text": f"Please create a task schedule based on the following input: {json.dumps(input_data.dict())}"}]},
        #     ],
        #     "model": MODEL_NAME,
        #     "temperature": 0.1
        # }

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

            # Store the generated schedule in memory and return it
            schedule_id = str(uuid.uuid4())
            saved_schedule[schedule_id] = {
                "schedule": schedule_data["schedule"],
                "notes": schedule_data.get("notes", "")
            }

            return OutputSchema(schedule_id=schedule_id, schedule=schedule_data["schedule"], notes=schedule_data.get("notes", ""))

        else:
            raise HTTPException(status_code=400, detail="No response text received from Gemini.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheduling failed: {str(e)}")

# PUT endpoint to update a task in the schedule
@app.put("/schedule/{schedule_id}/task/{task_id}")
async def update_task(schedule_id: str, task_id: str, updated_task: ScheduleItem):
    if schedule_id not in saved_schedule:
        return {"message": "Schedule not found"}

    schedule = saved_schedule[schedule_id]["schedule"]

    for idx, task in enumerate(schedule):
        if task.task_id == task_id:
            schedule[idx] = updated_task
            return {"message": "Task updated", "updated_task": updated_task}

    return {"message": "Task not found in the schedule"}

# GET endpoint to fetch the schedule by ID
@app.get("/schedule/{schedule_id}", response_model=OutputSchema)
async def get_schedule(schedule_id: str):
    try:
        if schedule_id not in saved_schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        schedule_data = saved_schedule[schedule_id]
        return OutputSchema(schedule_id=schedule_id, schedule=schedule_data["schedule"], notes=schedule_data.get("notes", ""))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schedule: {str(e)}")

# Function to query Gemini model
@app.post("/gemini/query")
async def query_gemini_model(request: Dict[str, Any]) -> Dict[str, Any]:
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds
    today = datetime.date.today()
    current_hour = datetime.datetime.now().time()
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

                If a task's duration exceeds any contiguous block of time available in a given day, just schedule it in the next day at . Every task must be scheduled EXACTLY ONCE!
                The task that appeared next day should be limit by working_hours and workdays and breaks and priority.

                starting date of the task should next week (today is {today.strftime("%Y-%m-%d")}) 
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