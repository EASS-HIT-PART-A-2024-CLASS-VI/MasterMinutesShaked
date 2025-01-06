from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import json
import os
from typing import Dict, Any
import uvicorn
import time
from moudles import InputSchema, OutputSchema, ScheduleItem
import uuid
from moudles import Task
import uuid
import asyncio
import google.generativeai as genai



app = FastAPI()


# Load Google Gemini API key
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "key")
if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")
genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-pro"
# In-memory storage for GET endpoint
saved_schedule = {}
schedules=[]


class GeminiQueryRequest(BaseModel):
    messages: list
    model: str = MODEL_NAME #defaulting to gemini pro
    temperature: float = 0.5


@app.post("/schedule", response_model=OutputSchema)
async def generate_schedule(input_data: InputSchema):
    try:
        # Attempt to query the external API
        gemini_input = {
            "messages": [
                {"role": "user", "parts": [{"text": f"Please assist in scheduling tasks. here is a json containing my tasks {json.dumps(input_data.dict())}"}]},
            ],
            "model": MODEL_NAME,
            "temperature": 0.5
        }
        try:
            gemini_response = await query_gemini_model(request=GeminiQueryRequest(**gemini_input))
            response_text = gemini_response.get("response_text", None)
            xai_suggestions = []
            if response_text:
                # Attempt to load JSON if text is available
                 try:
                    xai_suggestions=json.loads(response_text)
                 except json.JSONDecodeError:
                    print("Failed to parse the model's output as JSON, using the original tasks instead.")
                    xai_suggestions= input_data.tasks
                 #if json was successfully parsed, we can sort by priority
            else:
                xai_suggestions = input_data.tasks
        except HTTPException as e:
            if e.status_code == 429:
                # Fallback logic for local scheduling
                xai_suggestions = input_data.tasks
            else:
                raise e

        # Use the suggestions from the API or the fallback tasks
        tasks = sorted(
            xai_suggestions,
            key=lambda t: {"high": 3, "medium": 2, "low": 1}.get(t.priority, 0),
            reverse=True
        )

        # Scheduling logic...
        return await schedule_tasks(tasks, input_data.constraints)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheduling failed: {str(e)}")


@app.put("/schedule/{schedule_id}/task/{task_id}")
async def update_task(schedule_id: str, task_id: str, updated_task: ScheduleItem):
    # Check if the schedule exists
    if schedule_id not in saved_schedule:
        return {"message": "Schedule not found"}

    # Access the schedule
    schedule = saved_schedule[schedule_id]["schedule"]

    # Find and update the specific task by task_id
    for idx, task in enumerate(schedule):
        if task.task_id == task_id:  # Match task_id
            schedule[idx] = updated_task  # Replace the task
            return {"message": "Task updated", "updated_task": updated_task}

    # If task_id is not found
    return {"message": "Task not found in the schedule"}


@app.get("/schedule/{schedule_id}", response_model=OutputSchema)
async def get_schedule(schedule_id: str):
    """
    Endpoint to fetch the schedule by ID.
    """
    try:
        # Check if the schedule_id exists in the saved_schedule dictionary
        if schedule_id not in saved_schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        # Retrieve the schedule and notes from the saved_schedule
        schedule_data = saved_schedule[schedule_id]
        schedule = schedule_data.get("schedule", [])
        notes = schedule_data.get("notes", "")
        #
        # Return the schedule with the schedule_id
        return OutputSchema(schedule_id=schedule_id, schedule=schedule, notes=notes)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schedule: {str(e)}")


@app.post("/gemini/query")
async def query_gemini_model(request: GeminiQueryRequest) -> Dict[str, Any]:
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds

    model = genai.GenerativeModel(request.model)

    for attempt in range(MAX_RETRIES):
        try:
            
            # Adjust the prompt to use the new structure
            messages=[{'role': 'user', 'parts': [{'text': message['parts'][0]['text']}]} for message in request.messages]
            
            response = model.generate_content(messages, generation_config={"temperature": request.temperature})
            
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


async def schedule_tasks(tasks: List[Task], constraints: dict) -> OutputSchema:
     # Initialize an empty schedule and other necessary variables
    schedule: List[ScheduleItem] = []
    current_time = datetime.now()
    last_end_time = current_time
    
    # Get daily start and end time from constraints, default to 9 am and 5 pm if not provided
    start_time_str = constraints.get("daily_start_time", "09:00")
    end_time_str = constraints.get("daily_end_time", "17:00")

    # Parse start and end times
    try:
      start_time = datetime.strptime(start_time_str, '%H:%M').time()
      end_time = datetime.strptime(end_time_str, '%H:%M').time()
    except ValueError as e:
      raise HTTPException(status_code=400, detail=f"Invalid time format in constraints: {str(e)}")

    # Convert the string representations of breaks into datetime.time
    breaks = []
    if "breaks" in constraints:
      for brk in constraints["breaks"]:
            try:
                 break_start_time = datetime.strptime(brk['start'], '%H:%M').time()
                 break_end_time = datetime.strptime(brk['end'], '%H:%M').time()
                 breaks.append({'start':break_start_time, 'end':break_end_time})
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid time format in constraints: {str(e)}")
    
    # Get workdays
    workdays = constraints.get("workdays", ["SUN","MON","TUE","WED","THU","FRI","SAT"])

    # Handle multiple days and dates here
    for task in tasks:
      task_duration_hours = task.duration_minutes / 60.0
      
      # Calculate the start time based on the last end time
      task_start_time = last_end_time

      # Check if the task_start_time is within the working hours
      if task_start_time.time() < start_time:
        task_start_time = task_start_time.replace(hour=start_time.hour, minute=start_time.minute)

       # Adjust if the last_end_time falls outside work hours
      if last_end_time.time() >= end_time:
        last_end_time = last_end_time.replace(hour=start_time.hour, minute=start_time.minute)
        last_end_time += timedelta(days=1)  # Move to next day
      
      # Ensure that the task is within the workdays
      while task_start_time.strftime("%a").upper() not in workdays:
         task_start_time += timedelta(days=1)
         last_end_time = task_start_time
         

      
      task_end_time = task_start_time + timedelta(hours=task_duration_hours)
      
      # Ensure task doesn't overlap breaks
      for brk in breaks:
            break_start = task_start_time.replace(hour=brk['start'].hour, minute=brk['start'].minute, second=0, microsecond=0)
            break_end = task_start_time.replace(hour=brk['end'].hour, minute=brk['end'].minute, second=0, microsecond=0)
            if break_start < task_end_time and break_end > task_start_time:
                # Move the task after the break
                task_start_time = break_end
                task_end_time = task_start_time + timedelta(hours=task_duration_hours)

      
      if task_end_time.time() > end_time:
         # Move the task to the next day and set to start of day
          task_start_time = task_start_time.replace(hour=start_time.hour, minute=start_time.minute)
          task_start_time += timedelta(days=1)
          
          #Ensure that the task is within the workdays
          while task_start_time.strftime("%a").upper() not in workdays:
             task_start_time += timedelta(days=1)

          task_end_time = task_start_time + timedelta(hours=task_duration_hours)

      last_end_time = task_end_time
    # Append new schedule item to schedule list
      new_schedule_item = ScheduleItem(
        task_id=str(uuid.uuid4()),
        task_name=task.name,
        start_time=task_start_time.isoformat(),
        end_time=task_end_time.isoformat(),
        priority = task.priority,
        notes=task.notes
      )
      schedule.append(new_schedule_item)
    
    schedule_id = str(uuid.uuid4())

    saved_schedule[schedule_id] = {
    "schedule": schedule,
    "notes": ""
}

    return OutputSchema(schedule_id=schedule_id, schedule=schedule, notes="")




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
