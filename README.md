
# 📅MasterMinutes: A LLM-Powered Task Scheduler Application
MasterMinutes is an AI-powered Pomodoro-based task scheduling application that helps you stay focused and productive. Leveraging advanced LLM capabilities, it intelligently organizes your tasks, optimizes work sessions, and provides smart recommendations to enhance time management. Whether you're tackling deep work, managing multiple projects, or simply aiming to boost efficiency, MasterMinutes ensures you make the most of every minute.
---
## 📊 Project Diagram

![Project Diagram](./diagram.png)

## 📁 Project Structure
 
```
.
.
├── backend/
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── telegram_service.py
│   ├── tests/
│      ├── __init__.py
│      └── test_llm.py
├── docker-compose.yml
├── Dockerfile-fastapi
├── Dockerfile-telegram
│   ├─react-frontend/
│   │   ├── public/
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── Dashboard.js
│   │   │   │   ├── TaskForm.js
│   │   │   │   ├── TaskList.js
│   │   │   │   ├── ScheduleForm.js
│   │   │   │   └── ScheduleViewer.js
│   │   │   ├── services/
│   │   │   │   ├── api.js
│   │   │   │   └── telegramApi.js
│   │   │   ├── App.js
│   │   │   └── index.js
│   │   ├── .gitignore
│   │   ├── package.json
│   │   └── README.md
│   ├── streamlit_app.py
│   └── streamlit_requirements.txt
├── .env
├── .envExample
├── .gitignore
├── README.md
├── requirements.txt
├── run_tests.sh
└── test.db
```

- **`main.py`**: Defines API endpoints and contains scheduling logic.
- **`moudles.py`**: Houses SQLAlchemy models and Pydantic schemas for request and response validation.
- **`test_llm.py`**: Contains automated test cases for API functionality.
- **`run_tests.sh`**: A shell script to automate testing.
- **`requirements.txt`**: Lists all required Python dependencies for the project.
- **`Dockerfile-fastapi`**: Contains instructions to containerize the FastAPI backend.
- **`Dockerfile-telegram`**: Contains instructions to containerize the Telegram service.
- **`README.md`**: Comprehensive guide to the project.

---


## ⚙️ API Endpoints Overview

| **Method** | **Endpoint**                                   | **Description**                                                                 |
|------------|-----------------------------------------------|---------------------------------------------------------------------------------|
| **POST**   | `/schedule`                                   | Generates a task schedule using Gemini or a fallback local scheduler.          |
| **GET**    | `/schedule/{schedule_id}`                     | Retrieves a schedule by its unique ID.                                         |
| **PUT**    | `/schedule/{schedule_id}/task/{task_id}`      | Updates a specific task within a schedule.                                     |
| **POST**   | `/gemini/query`                               | Queries the Gemini LLM to generate a JSON schedule.                            |
| **POST**   | `/register`                                   | Registers a new user account.                                                  |
| **POST**   | `/token`                                      | Authenticates a user and returns an access token.                              |
| **GET**    | `/users/me`                                   | Retrieves the currently authenticated user's information.                       |
| **GET**    | `/get_schedule/{schedule_id}`                 | Fetches the schedule and sends it to the user's Telegram chat.                 |


---

## 📌 Endpoint Details

### **1. POST `/schedule`**

**Description:** Generates a task schedule using an LLM or fallback scheduler.

#### Request Body:
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

#### Response Body:
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

---

### **2. GET `/schedule/{schedule_id}`**

**Description:** Fetches a schedule by its ID.

#### Path Parameter:
- **`schedule_id`**: Unique identifier of the schedule.

#### Response Body:
Same as the **`POST /schedule`** response.

---

### **3. PUT `/schedule/{schedule_id}/task/{task_id}`**

**Description:** Updates a specific task within a schedule.

#### Path Parameters:
- **`schedule_id`**: Unique schedule identifier.
- **`task_id`**: Unique task identifier.

#### Request Body:
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

#### Response Body:
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

---

## 🚀 How to Run

1. **Clone the repository:**
   ```bash
   git clone [repository_url]
   cd [repository_directory]
   ```

2. **Set up the environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # Linux/macOS
   # venv\Scripts\activate    # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   ```bash
   export GOOGLE_API_KEY="your_gemini_api_key"
   export REDIS_URL=redis_url
   export TELEGRAM_TOKEN="your_telegram_bot_token"
   export TELEGRAM_CHAT_ID="your_telegram_chat_id"
   ```

5. **Run the application:**
   ```bash
   uvicorn main:app --port 1236 --reload
   ```

6. **Run tests:**
   ```bash
   chmod +x run_tests.sh
   ./run_tests.sh
   ```

7. **Access the API Docs:**
   Navigate to **[http://127.0.0.1:1236/docs](http://127.0.0.1:1236/docs)** for Swagger UI.

---

## 🐳 Running with Docker

1. **Build the Docker image:**
   ```bash
   docker build -t masterminutes-api .
   ```

2. **Run the container:**
   ```bash
   docker run -p 1236:1236 masterminutes-api
   ```

3. **Access the API Docs:**
   Visit **[http://127.0.0.1:1236/docs](http://127.0.0.1:1236/docs)**.

---

## 🧪 Running Tests

To validate the functionality:
```bash
./run_tests.sh
```
This script:
- Starts the application.
- Runs all test cases.
- Shuts down the application.

---
