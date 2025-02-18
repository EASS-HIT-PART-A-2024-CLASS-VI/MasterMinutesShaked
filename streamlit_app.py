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
def create_schedule(tasks, constraints, working_days, start_hour_day, end_hour_day, breaks):
    payload = {
        "tasks": tasks,
        "constraints": constraints,
        "working_days": working_days,
        "start_hour_day": start_hour_day,
        "end_hour_day": end_hour_day,
        "Breaks": breaks
    }
    try:
        response = requests.post(f"{API_URL}/schedule", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to create schedule: {e}")
        return None

# Inject custom CSS to change the background color to white
st.markdown(
    """
    <style>
    .main {
        background-color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit application title
st.title("Task Scheduler")

# Sidebar for adding tasks
st.sidebar.header("Add a New Task")
task_name = st.sidebar.text_input("Task Name")
task_duration = st.sidebar.number_input("Duration (in minutes)", min_value=1)
task_priority = st.sidebar.selectbox("Priority", ["High", "Medium", "Low"])
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
        st.write(f"{i+1}. {task['name']} - {task['duration_minutes']} minutes - {task['priority']} priority")
else:
    st.write("No tasks added yet.")

# Input form for scheduling constraints
st.sidebar.header("Scheduling Constraints")
start_hour_day = st.sidebar.text_input("Start Hour of Day (HH:MM)", value="09:00")
end_hour_day = st.sidebar.text_input("End Hour of Day (HH:MM)", value="17:00")
working_days = st.sidebar.multiselect("Working Days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
constraints = st.sidebar.text_area("Constraints (JSON format)", value="{}")
breaks = st.sidebar.text_area("Breaks (JSON format)", value="[]")
schedule_button = st.sidebar.button("Create Schedule")

if schedule_button:
    try:
        constraints_dict = json.loads(constraints)
        breaks_list = json.loads(breaks)
        schedule = create_schedule(st.session_state["tasks"], constraints_dict, working_days, start_hour_day, end_hour_day, breaks_list)
        if schedule:
            print("scheduleeeee:" + json.dumps(schedule))
            st.success("Schedule created successfully!")
            st.json(schedule)
    except json.JSONDecodeError as e:
        st.sidebar.error(f"Invalid JSON format: {e}")

# Display the schedule
st.header("Schedule")
schedule_id = st.text_input("Enter Schedule ID to fetch")
fetch_button = st.button("Fetch Schedule")

if fetch_button and schedule_id:
    schedule = get_schedule(schedule_id)
    if schedule:
        st.json(schedule)