import requests
import json
import pytest
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:1236"  # Replace if your app runs on a different host/port

@pytest.fixture(scope="session")
def access_token():
    # Register a new user
    register_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    }
    headers = {'Content-Type': 'application/json'}
    register_response = requests.post(f"{BASE_URL}/register", headers=headers, data=json.dumps(register_data))
    assert register_response.status_code == 200

    # Obtain the access token
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    login_response = requests.post(f"{BASE_URL}/token", data=login_data)
    assert login_response.status_code == 200
    token_data = login_response.json()
    return token_data["access_token"]

def test_generate_schedule_success(access_token):
    input_data = {
        "tasks": [
            {
                "name": "Task 1",
                "duration_minutes": 90,
                "priority": "high",
                "notes": "Test task 1"
            },
            {
                "name": "Task 2",
                "duration_minutes": 60,
                "priority": "medium",
                "notes": "Test task 2"
            }
        ],
        "working_days": [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
        ],
        "start_hour_day": "09:00",
        "end_hour_day": "17:00",
        "constraints": {},
        "Breaks": [
                {
                    "start": "12:00",
                    "end": "13:00"
                }
        ]
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.post(f"{BASE_URL}/schedule", headers=headers, data=json.dumps(input_data))
    assert response.status_code == 200
    response_json = response.json()
    assert "schedule" in response_json
    assert "schedule_id" in response_json
    assert isinstance(response_json["schedule"], list)

    first_task = response_json["schedule"][0]
    assert "task_id" in first_task
    assert "task_name" in first_task
    assert "start_time" in first_task
    assert "end_time" in first_task
    assert "priority" in first_task

    # Check to see if the first task is within the given constraints
    start_time = datetime.strptime(first_task['start_time'], "%H:%M").time()
    daily_start_time = datetime.strptime("09:00", "%H:%M").time()
    daily_end_time = datetime.strptime("17:00", "%H:%M").time()
    assert start_time >= daily_start_time
    assert start_time < daily_end_time

def test_get_schedule_success(access_token):
    # First, generate a schedule
    input_data = {
        "tasks": [
            {
                "name": "Task 1",
                "duration_minutes": 60,
                "priority": "high",
                "notes": "Test task 1"
            }
        ],
        "working_days": [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
        ],
        "start_hour_day": "09:00",
        "end_hour_day": "17:00",
        "constraints": {},
        "Breaks": [
                {
                    "start": "12:00",
                    "end": "13:00"
                }
        ]

    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    post_response = requests.post(f"{BASE_URL}/schedule", headers=headers, data=json.dumps(input_data))
    assert post_response.status_code == 200
    schedule_id = post_response.json()["schedule_id"]
    # Now, get the schedule
    get_response = requests.get(f"{BASE_URL}/schedule/{schedule_id}", headers=headers)
    assert get_response.status_code == 200
    get_response_json = get_response.json()
    assert "schedule" in get_response_json
    assert "schedule_id" in get_response_json
    assert schedule_id == get_response_json["schedule_id"]

def test_get_schedule_not_found(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    get_response = requests.get(f"{BASE_URL}/schedule/non_existent_id", headers=headers)
    assert get_response.status_code == 404




def test_update_task_success(access_token):
    # First, generate a schedule
    input_data = {
        "tasks": [
            {
                "name": "Task 1",
                "duration_minutes": 60,
                "priority": "high",
                "notes": "Test task 1"
            }
        ],
        "working_days": [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
        ],
        "start_hour_day": "09:00",
        "end_hour_day": "17:00",
        "constraints": {},
        "Breaks": [
                {
                    "start": "12:00",
                    "end": "13:00"
                }
        ]

    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    post_response = requests.post(f"{BASE_URL}/schedule", headers=headers, data=json.dumps(input_data))
    assert post_response.status_code == 200
    schedule_id = post_response.json()["schedule_id"]
    task_id = post_response.json()["schedule"][0]["task_id"]


    updated_task_data = {
        "task_id": task_id,
        "task_name": "Updated Task 1",
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
        "day": "Monday",
        "date": "2025-02-26",
        "priority": "low",
        "notes": "Updated notes"
    }

    # Now, update the schedule
    put_response = requests.put(f"{BASE_URL}/schedule/{schedule_id}/task/{task_id}", headers=headers, data=json.dumps(updated_task_data))
    assert put_response.status_code == 200
    put_response_json = put_response.json()
    assert "updated_task" in put_response_json
    assert put_response_json["updated_task"]["task_name"] == "Updated Task 1"
    assert put_response_json["updated_task"]["priority"] == "low"

def test_update_task_not_found(access_token):

    updated_task_data = {
        "task_id": "non_existent_id",
        "task_name": "Updated Task 1",
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
        "day": "Monday",
        "date": "2025-02-26",
        "priority": "low",
        "notes": "Updated notes"
    }


    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    put_response = requests.put(f"{BASE_URL}/schedule/non_existent_schedule/task/non_existent_id", headers=headers, data=json.dumps(updated_task_data))
    assert put_response.status_code == 404
    assert put_response.json() == {"detail": "Task not found"}