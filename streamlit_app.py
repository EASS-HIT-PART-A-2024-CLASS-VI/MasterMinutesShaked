import streamlit as st
import requests
from datetime import datetime, timedelta
import json

# Base URL of the FastAPI backend
API_URL = "http://fastapi:1236"

# Function to get schedule by ID
def get_schedule(schedule_id):
    try:
        response = requests.get(f"{API_URL}/schedule/{schedule_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch schedule: {e}")
        return None

# Function to create a new schedule
def create_schedule(tasks, constraints):
    payload = {
        "tasks": tasks,
        "constraints": constraints
    }
    try: 
        st.error(payload)
        response = requests.post(f"{API_URL}/schedule", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to create schedule: {e}")
        return None

# Streamlit UI
st.title("Task Scheduler with Gemini LLM")

# Sidebar for adding tasks
st.sidebar.header("Add Task")
task_name = st.sidebar.text_input("Task Name")
task_duration = st.sidebar.number_input("Duration (minutes)", min_value=1, step=1)
task_priority = st.sidebar.selectbox("Priority", ["low", "medium", "high"])
task_notes = st.sidebar.text_area("Notes (optional)")
add_task = st.sidebar.button("Add Task")

# Store tasks in session state
if "tasks" not in st.session_state:
    st.session_state["tasks"] = []
    st.session_state["breaks"] = []

if add_task:
    if task_name and task_duration:
        task = {
            "name": task_name,
            "duration_minutes": task_duration,
            "priority": task_priority,
            "notes": task_notes
        }
        st.session_state["tasks"].append(task)
        st.sidebar.success(f"Task '{task_name}' added!")
    else:
        st.sidebar.error("Please fill in all required fields.")

# Display added tasks
st.subheader("Tasks to Schedule")
if st.session_state["tasks"]:
    for i, task in enumerate(st.session_state["tasks"]):
        st.write(f"**Task {i+1}:** {task['name']} | Duration: {task['duration_minutes']} mins | Priority: {task['priority']}")
else:
    st.info("No tasks added yet.")

# Constraints form
st.subheader("Constraints")
daily_start_time = st.time_input("Daily Start Time", value=datetime.now().replace(hour=9, minute=0).time())
daily_end_time = st.time_input("Daily End Time", value=datetime.now().replace(hour=17, minute=0).time())
workdays = st.multiselect("Workdays", ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"], default=["MON", "TUE", "WED", "THU", "FRI"])
breaks = []
st.write("Breaks (optional)")
break_start_time = st.time_input("Break Start Time", value=None)
break_end_time = st.time_input("Break End Time", value=None)
if st.button("Add Break"):
    st.success(f'{break_start_time}, {break_end_time}')
    if break_start_time and break_end_time:
        st.session_state["breaks"].append({"start": break_start_time.strftime("%H:%M"), "end": break_end_time.strftime("%H:%M")})
        st.success(f"Break added. {st.session_state['breaks']}")
    else:
        st.error("Please provide both start and end times for the break.")
# st.success(f"Breaks: {breaks}")

# Submit button
if st.button("Generate Schedule"):
    # st.success(f"Breaks: {breaks}")
    constraints = {
        "daily_start_time": daily_start_time.strftime("%H:%M"),
        "daily_end_time": daily_end_time.strftime("%H:%M"),
        "workdays": workdays,
        "breaks": st.session_state["breaks"]
    }

    st.success(f"{constraints}")
    


    result = create_schedule(st.session_state["tasks"], constraints)
    if result:
        st.success("Schedule created successfully!")
        schedule_id = result.get("schedule_id")
        st.write(f"**Schedule ID:** {schedule_id}")
        st.session_state["current_schedule_id"] = schedule_id

# Display schedule if generated
if "current_schedule_id" in st.session_state:
    st.subheader("Generated Schedule")
    schedule = get_schedule(st.session_state["current_schedule_id"])
    if schedule:
        for item in schedule["schedule"]:
            st.write(f"**Task:** {item['task_name']} | **Start:** {item['start_time']} | **End:** {item['end_time']} | **Priority:** {item['priority']}")
