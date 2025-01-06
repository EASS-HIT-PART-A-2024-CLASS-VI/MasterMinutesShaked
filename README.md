# 📅 MasterMinutes: A LLM-Powered Task Scheduler API

A FastAPI-based project that leverages a Large Language Model (LLM) to intelligently schedule tasks based on user-defined constraints. This project aims to automate the task scheduling process, making it more efficient and adaptable.

## 📁 Project Structure

```
├── main.py # Main FastAPI application file
├── moudles.py # Pydantic models for data validation
├── test_llm.py # Pytest test suite for the API
├── run_tests.sh # Shell script to run tests
└── README.md # This file
```

* `main.py`: Contains the core logic of the FastAPI application, including API endpoints and scheduling logic.
* `moudles.py`: Defines the Pydantic models for request and response data validation.
* `test_llm.py`: Contains tests that validate the various functionalities of the program.
* `run_tests.sh`: A shell script for starting the API and executing the tests.
* `README.md`: Provides essential information about the project.

## ⚙️ API Endpoints Overview

| Method | Endpoint | Description | Request Body | Response Body |
|--------|----------|-------------|--------------|---------------|
| POST | `/schedule` | Generates a task schedule using an LLM or falls back to a local scheduler. | JSON object containing `tasks`, `constraints`, and optional `working_days` | JSON object containing `schedule_id`, `schedule` array, and `notes`. |
| GET | `/schedule/{schedule_id}` | Fetches a schedule based on its ID. | None | JSON object containing `schedule_id`, `schedule` array, and `notes`. |
| PUT | `/schedule/{schedule_id}/task/{task_id}` | Updates a specific task within a schedule using the provided `task_id` and `schedule_id`. | JSON object containing `task_id`, `task_name`, `start_time`, `end_time`, `priority` and `notes`. | JSON object with the `message` string `"Task updated"` along with the full updated `task` object. |

## ⚙️ API Endpoints Details

### 📌 POST `/schedule`

* **Description:** Generates a task schedule using an LLM or falls back to a local scheduler.
* **Request Body (JSON):**
```json
{
    "tasks": [
        {
            "name": "string",
            "duration_minutes": 0,
            "priority": "string",
            "notes": "string"
        }
    ],
    "constraints": {
        "daily_start_time": "string (HH:MM)",
        "daily_end_time": "string (HH:MM)",
        "breaks": [
            {
                "start": "string (HH:MM)",
                "end": "string (HH:MM)"
            }
        ],
        "workdays": ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `tasks` | `Array` | List of task objects |
| `tasks[].name` | `string` | Name of the task |
| `tasks[].duration_minutes` | `integer` | Duration of the task in minutes |
| `tasks[].priority` | `string` | Priority of the task (`high`, `medium`, or `low`) |
| `tasks[].notes` | `string` | Optional notes for the task |
| `constraints` | `Object` | Constraints for scheduling, like working hours and breaks |
| `constraints.daily_start_time` | `string` | The start of the working hours. Format: `HH:MM` |
| `constraints.daily_end_time` | `string` | The end of the working hours. Format: `HH:MM` |
| `constraints.breaks` | `Array` | Optional array of break periods |
| `constraints.breaks[].start` | `string` | Start of a break. Format: `HH:MM` |
| `constraints.breaks[].end` | `string` | End of a break. Format: `HH:MM` |
| `constraints.workdays` | `Array` | Optional array of working days. Allowed values: `SUN`, `MON`, `TUE`, `WED`, `THU`, `FRI`, `SAT`, defaults to all days |

* **Response (JSON):**
```json
{
    "schedule_id": "string (UUID)",
    "schedule": [
        {
            "task_id": "string (UUID)",
            "task_name": "string",
            "start_time": "string (ISO format)",
            "end_time": "string (ISO format)",
            "priority": "string",
            "notes": "string"
        }
    ],
    "notes": "string"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `schedule_id` | `string` | Unique identifier for the generated schedule |
| `schedule` | `Array` | List of scheduled task objects |
| `schedule[].task_id` | `string` | Unique identifier for the task |
| `schedule[].task_name` | `string` | Name of the scheduled task |
| `schedule[].start_time` | `string` | Start time of the scheduled task in ISO format |
| `schedule[].end_time` | `string` | End time of the scheduled task in ISO format |
| `schedule[].priority` | `string` | Priority of the scheduled task (`high`, `medium`, or `low`) |
| `schedule[].notes` | `string` | Optional notes for the scheduled task |
| `notes` | `string` | Optional notes for the schedule |

### 📌 GET `/schedule/{schedule_id}`

* **Description:** Fetches a schedule based on its ID.
* **Path Parameters:**
  * `schedule_id` (`string`): The unique identifier of the schedule.
* **Response (JSON):** Same as the response of `POST /schedule` above.
* **Error Response:**
  * 404 Not Found: If the schedule with the given `schedule_id` is not found.

### 📌 PUT `/schedule/{schedule_id}/task/{task_id}`

* **Description:** Updates a specific task within a schedule.
* **Path Parameters:**
  * `schedule_id` (`string`): The unique identifier of the schedule.
  * `task_id` (`string`): The unique identifier of the task within the schedule.
* **Request Body (JSON):**
```json
{
    "task_id": "string (UUID)",
    "task_name": "string",
    "start_time": "string (ISO format)",
    "end_time": "string (ISO format)",
    "priority": "string",
    "notes": "string"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | `string` | Unique identifier for the task to be updated |
| `task_name` | `string` | Updated name of the task |
| `start_time` | `string` | Updated start time of the task in ISO format |
| `end_time` | `string` | Updated end time of the task in ISO format |
| `priority` | `string` | Updated priority of the task (`high`, `medium`, or `low`) |
| `notes` | `string` | Updated optional notes for the task |

* **Response (JSON):**
```json
{
    "message": "Task updated",
    "updated_task": {
        "task_id": "string (UUID)",
        "task_name": "string",
        "start_time": "string (ISO format)",
        "end_time": "string (ISO format)",
        "priority": "string",
        "notes": "string"
    }
}
```

* **Error Response:**
  * 200 OK: If the `schedule_id` is not found, a message will be sent stating "Schedule not found".
  * 200 OK: If the `task_id` is not found, a message will be sent stating "Task not found in the schedule".

### ⚙️ `/gemini/query`

* **Description:** Queries the Gemini API for task suggestions. This endpoint is not directly used for scheduling, but can be used for model testing.
* **Request Body (JSON):**
```json
{
    "messages": [
        {
            "role": "user",
            "parts": [{"text": "string"}]
        }
    ],
    "model": "string (model name)",
    "temperature": 0.5
}
```
* `messages`: An array of messages that can be passed to Gemini.
* `model`: Which Gemini model to use.
* `temperature`: The sampling temperature to use for the model.

* **Response (JSON):**
```json
{
    "response_text": "string"
}
```
`response_text` contains the raw text response from the model

## 🚀 How to Run

Clone the repository:
```bash
git clone [repository_url]
cd [repository_directory]
```

Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate   # On Linux/macOS
# venv\Scripts\activate  # On Windows
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Note: you can create a requirements.txt by doing `pip freeze > requirements.txt` in your virtual environment

Set up environment variables:

Set your Google Gemini API key as an environment variable `GOOGLE_API_KEY`.
```bash
export GOOGLE_API_KEY="your_gemini_api_key"
```

Run the application:
```bash
uvicorn main:app --port 1236 --reload
```

Run the tests:
```bash
chmod +x run_tests.sh
./run_tests.sh
```

Access the API documentation at http://127.0.0.1:1236/docs

## 🧪 Running Tests

To validate the functionality, run the provided test script by running `./run_tests.sh`.
This will start the application, execute the tests, and then shutdown the application.

## 📜 License

This project is licensed under the [Your License] License - see the LICENSE.md file for details.