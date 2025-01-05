import requests
import json
import pytest
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:1236"  # Replace if your app runs on a different host/port


def test_generate_schedule_with_gemini_success():
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
        "constraints": {
          "daily_start_time": "09:00",
          "daily_end_time": "17:00",
            "breaks": [
                {
                   "start": "12:00",
                   "end": "13:00"
                }
            ]
        }
    }
    headers = {'Content-Type': 'application/json'}

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
    
    #Check to see if the first task is within the given constraints
    start_time = datetime.fromisoformat(first_task["start_time"]).time()
    daily_start_time = datetime.strptime("09:00", "%H:%M").time()
    daily_end_time = datetime.strptime("17:00", "%H:%M").time()
    assert start_time >= daily_start_time
    assert start_time < daily_end_time

def test_get_schedule_success():
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
       "constraints": {
           "daily_start_time": "09:00",
           "daily_end_time": "17:00"
         }
    }
    headers = {'Content-Type': 'application/json'}
    post_response = requests.post(f"{BASE_URL}/schedule", headers=headers, data=json.dumps(input_data))
    assert post_response.status_code == 200
    schedule_id = post_response.json()["schedule_id"]

    # Now, get the schedule
    get_response = requests.get(f"{BASE_URL}/schedule/{schedule_id}")
    assert get_response.status_code == 200
    get_response_json = get_response.json()
    assert "schedule" in get_response_json
    assert "schedule_id" in get_response_json
    assert schedule_id == get_response_json["schedule_id"]

def test_get_schedule_not_found():
    get_response = requests.get(f"{BASE_URL}/schedule/non_existent_id")
    assert get_response.status_code == 404

def test_update_task_success():
   #First, generate a schedule
   input_data = {
     "tasks": [
          {
             "name": "Task 1",
             "duration_minutes": 60,
             "priority": "high",
             "notes": "Test task 1"
           }
        ],
        "constraints": {
           "daily_start_time": "09:00",
           "daily_end_time": "17:00"
         }
   }
   headers = {'Content-Type': 'application/json'}
   post_response = requests.post(f"{BASE_URL}/schedule", headers=headers, data=json.dumps(input_data))
   assert post_response.status_code == 200
   schedule_id = post_response.json()["schedule_id"]
   task_id = post_response.json()["schedule"][0]["task_id"]
   
   updated_task_data = {
         "task_id": task_id,
         "task_name": "Updated Task 1",
         "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
         "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
         "priority": "low",
         "notes": "Updated notes"
   }
   
   #Now, update the schedule
   put_response = requests.put(f"{BASE_URL}/schedule/{schedule_id}/task/{task_id}", headers=headers, data=json.dumps(updated_task_data))
   assert put_response.status_code == 200
   put_response_json = put_response.json()
   assert "updated_task" in put_response_json
   assert put_response_json["updated_task"]["task_name"] == "Updated Task 1"
   assert put_response_json["updated_task"]["priority"] == "low"

def test_update_task_not_found():
    updated_task_data = {
         "task_id": "non_existent_id",
         "task_name": "Updated Task 1",
         "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
         "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
         "priority": "low",
         "notes": "Updated notes"
     }

    headers = {'Content-Type': 'application/json'}
    put_response = requests.put(f"{BASE_URL}/schedule/non_existent_schedule/task/non_existent_id", headers=headers, data=json.dumps(updated_task_data))
    assert put_response.status_code == 200
    assert put_response.json() == {"message": "Schedule not found"}