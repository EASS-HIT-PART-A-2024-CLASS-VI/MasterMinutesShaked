from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import json
import os
from typing import Dict, Any
import httpx
import uvicorn
import time
from moudles import InputSchema, OutputSchema, ScheduleItem
import uuid
from moudles import Task
import uuid

app = FastAPI()
XAI_API_URL = "https://api.x.ai/v1/chat/completions"
XAI_API_KEY=os.getenv("XAI_API_KEY","xai-E1k9MfYkCYJpOjVDBApakzCDONYsB1Pa6bSpUB8WIKCnCPZZ5xVBKpL44qMQaKH7tGFE0uY4D7R22HM7")

# In-memory storage for GET endpoint
saved_schedule = {}
schedules=[]

class XAIQueryRequest(BaseModel):
    messages: list
    model: str = "grok-beta"
    stream: bool = False
    temperature: float = 0


@app.post("/schedule", response_model=OutputSchema)
async def generate_schedule(input_data: InputSchema):
    """
    Endpoint to generate a schedule based on tasks and constraints,
    possibly utilizing XAI API for task prioritization or assistance.
    """
    print(f"Received input_data: {input_data}")

    try:
        # Prepare data for the XAI model (e.g., task details, constraints)
        xai_input = {
            "messages": [
                {"role": "system", "content": "Please assist in scheduling tasks."},
                {"role": "user", "content": json.dumps(input_data.dict())}
            ],
            "model": "grok-beta",  # or the XAI model you are using
            "stream": False,
            "temperature": 0.5
        }

        # Query the XAI model for additional scheduling suggestions or prioritization
        xai_response = await query_xai_model(request=XAIQueryRequest(**xai_input))

        # Parse the XAI response (you can decide how to process the response)
        xai_suggestions = xai_response.get("suggestions", [])

        # If no suggestions from XAI, fall back to default logic
        if not xai_suggestions:
            xai_suggestions = input_data.tasks

        # Priority mapping for sorting
        priority_map = {
            "high": 3,
            "medium": 2,
            "low": 1
        }

        # Sort tasks based on priority
        tasks = sorted(xai_suggestions, key=lambda t: priority_map.get(t.priority, 0), reverse=True)

        constraints = input_data.constraints
        
        # Initialize start time
        current_time = datetime.strptime(constraints.work_hours_start, "%H:%M")
        work_end = datetime.strptime(constraints.work_hours_end, "%H:%M")
        breaks = [(datetime.strptime(b.start, "%H:%M"), datetime.strptime(b.end, "%H:%M")) for b in constraints.breaks]
        
        schedule = []
        notes = "High-priority tasks scheduled first. Breaks are included."

        for task in tasks:
            task_duration = timedelta(minutes=task.duration_minutes)
            
            # Adjust for breaks
            for break_start, break_end in breaks:
                if current_time >= break_start and current_time < break_end:
                    current_time = break_end

            # Ensure task fits in work hours
            if current_time + task_duration > work_end:
                notes = "Not all tasks could be scheduled within working hours."
                break
            
            # Schedule task
            end_time = current_time + task_duration
            schedule.append(ScheduleItem(
                task_id=task.id,
                start_time=current_time.strftime("%H:%M"),
                end_time=end_time.strftime("%H:%M")
            ))
            current_time = end_time  # Update current time
        
        # Generate a unique schedule ID (for example, using UUID)
        schedule_id = str(uuid.uuid4())

        # Save the generated schedule (You can store this in memory or a database)
        saved_schedule[schedule_id] = {
            "schedule": schedule,
            "notes": notes
        }

        # Return the schedule with the generated schedule_id
        return OutputSchema(schedule_id=schedule_id, schedule=schedule, notes=notes)

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

# @app.put("/schedule/{id}")
# async def update_schedule(id: str, todo_obj: ScheduleItem):  # Use ScheduleItem here
#     for schedule in saved_schedule.values():
#         for i,task in enumerate(schedule['schedule']):
#             if task.task_id == id:
#                 schedule['schedule'][i] = todo_obj  
#                 # task.name = todo_obj.name  # Update the name field
#                 # task.start_time = todo_obj.start_time
#                 # task.end_time = todo_obj.end_time
#                 # del schedule['schedule'][i]
#                 # schedule['schedule'][i].append(todo_obj)
#                 return {"message": "Schedule updated", "schedule": todo_obj}
#     return {"message": "Schedule not found"}


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


@app.post("/xai/query")
async def query_xai_model(request: XAIQueryRequest) -> Dict[str, Any]:
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {XAI_API_KEY}"
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(XAI_API_URL, headers=headers, json=request.dict())
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()  # Return the response as a JSON object
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="xAI API timeout")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
