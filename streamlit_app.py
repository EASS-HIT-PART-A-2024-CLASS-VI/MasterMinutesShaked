import streamlit as st
import requests
import json
import os

# Base URL of the FastAPI backend
API_URL = "http://fastapi:1236"
st.write("API URL:", API_URL)

# Initialize session state variables
if "token" not in st.session_state:
    st.session_state["token"] = None
if "tasks" not in st.session_state:
    st.session_state["tasks"] = []
if "breaks" not in st.session_state:
    st.session_state["breaks"] = []

# -------------------------------
# Helper: Safe rerun function
# -------------------------------
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.warning("Auto rerun is not supported by your Streamlit version. Please refresh the browser manually.")

# -------------------------------
# Authentication Functions
# -------------------------------
def login_user(username, password):
    st.write("Attempting to connect to:", f"{API_URL}/token")
    try:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        st.write("Response status code:", response.status_code)
        response.raise_for_status()
        token_data = response.json()
        st.write("Login successful, token received")
        return token_data["access_token"]
    except requests.exceptions.RequestException as e:
        st.error(f"Login failed: {str(e)}")
        st.write("Full error details:", e.__dict__)
        return None

def register_user(username, email, password):
    st.write("Attempting to register at:", f"{API_URL}/register")
    payload = {
        "username": username,
        "email": email,
        "password": password
    }
    try:
        response = requests.post(
            f"{API_URL}/register",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        st.write("Registration response status:", response.status_code)
        response.raise_for_status()
        user_data = response.json()
        st.write("Registration successful for user:", user_data)
        return user_data
    except requests.exceptions.RequestException as e:
        st.error(f"Registration failed: {e}")
        st.write("Full error details:", e.__dict__)
        return None

# -------------------------------
# Authentication UI: Only show if token is not set
# -------------------------------
if not st.session_state["token"]:
    auth_mode = st.sidebar.radio("Select Option", ["Login", "Register"])
    
    if auth_mode == "Login":
        st.title("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            token = login_user(username, password)
            if token:
                st.session_state["token"] = token
                st.success("Logged in successfully!")
                safe_rerun()  # Use safe rerun to refresh the app
            else:
                st.error("Invalid credentials. Please try again.")
    
    elif auth_mode == "Register":
        st.title("Register")
        reg_username = st.text_input("Username", key="reg_username")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
        if st.button("Register"):
            if reg_password != reg_password_confirm:
                st.error("Passwords do not match.")
            else:
                result = register_user(reg_username, reg_email, reg_password)
                if result:
                    st.success("Registration successful! Please log in.")
                    safe_rerun()  # Refresh to show login UI
    # Stop execution if the token is still not set
    if not st.session_state["token"]:
        st.stop()

# -------------------------------
# Main App: Task Scheduler
# -------------------------------
st.title("Task Scheduler")

# Sidebar for adding tasks
st.sidebar.header("Add a New Task")
task_name = st.sidebar.text_input("Task Name")
task_duration = st.sidebar.number_input("Duration (in minutes)", min_value=1)
task_priority = st.sidebar.selectbox("Priority", ["High", "Medium", "Low"])
task_notes = st.sidebar.text_area("Notes (optional)")
add_task = st.sidebar.button("Add Task")

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

st.subheader("Tasks to Schedule")
if st.session_state["tasks"]:
    for i, task in enumerate(st.session_state["tasks"]):
        st.write(f"{i+1}. {task['name']} - {task['duration_minutes']} minutes - {task['priority']} priority")
else:
    st.write("No tasks added yet.")

# Input form for scheduling constraints in the sidebar
st.sidebar.header("Scheduling Constraints")
start_hour_day = st.sidebar.text_input("Start Hour of Day (HH:MM)", value="09:00")
end_hour_day = st.sidebar.text_input("End Hour of Day (HH:MM)", value="17:00")
working_days = st.sidebar.multiselect(
    "Working Days",
    ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"],
    default=["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
)
constraints = st.sidebar.text_area("Constraints (JSON format)", value="{}")
breaks = st.sidebar.text_area("Breaks (JSON format)", value="[]")
schedule_button = st.sidebar.button("Create Schedule")

def create_schedule(tasks, constraints, working_days, start_hour_day, end_hour_day, breaks, token):
    payload = {
        "tasks": tasks,
        "constraints": constraints,
        "working_days": working_days,
        "start_hour_day": start_hour_day,
        "end_hour_day": end_hour_day,
        "Breaks": breaks
    }
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(f"{API_URL}/schedule", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to create schedule: {e}")
        return None

if schedule_button:
    try:
        constraints_dict = json.loads(constraints)
        breaks_list = json.loads(breaks)
        schedule = create_schedule(
            st.session_state["tasks"],
            constraints_dict,
            working_days,
            start_hour_day,
            end_hour_day,
            breaks_list,
            st.session_state["token"]
        )
        if schedule:
            st.success("Schedule created successfully!")
            st.json(schedule)
    except json.JSONDecodeError as e:
        st.sidebar.error(f"Invalid JSON format: {e}")

# Section to fetch and display a schedule by ID
st.header("Schedule")
schedule_id = st.text_input("Enter Schedule ID to fetch")
fetch_button = st.button("Fetch Schedule")

def get_schedule(schedule_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{API_URL}/schedule/{schedule_id}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch schedule: {e}")
        return None

if fetch_button and schedule_id:
    schedule = get_schedule(schedule_id, st.session_state["token"])
    if schedule:
        st.json(schedule)
