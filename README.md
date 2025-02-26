
# 📅 MasterMinutes: A LLM-Powered Task Scheduler API

A **FastAPI**-based project that leverages a **Large Language Model (LLM)** to intelligently schedule tasks based on user-defined constraints. This project automates and optimizes the scheduling process, making it more efficient and adaptable.

---
## 📊 Project Diagram

![Project Diagram](./diagram.png)

## 📁 Project Structure
 
```
.
├── __pycache__/                # Compiled Python files
├── .dockerignore               # Docker ignore file
├── .env                        # Environment variables file
├── .envExample                 # Example environment variables file
├── .gitignore                  # Git ignore file
├── .pytest_cache/              # Pytest cache directory
├── .vscode/                    # VSCode configuration directory
├── backend/                    # Backend directory
│   ├── __init__.py             # Backend package initializer
│   ├── auth/                   # Authentication module
│   │   ├── __init__.py
│   │   └── auth.py             # Authentication logic
│   ├── core/                   # Core application logic
│   │   ├── __init__.py
│   │   └── main.py             # Core FastAPI application file
│   ├── db/                     # Database configuration and models
│   │   ├── __init__.py
│   │   ├── database.py         # Database configuration
│   │   └── models.py           # SQLAlchemy models and Pydantic schemas
│   ├── services/               # Services and business logic
│   │   ├── __init__.py
│   │   └── telegram_service.py # Telegram service for sending notifications
│   ├── tests/                  # Test cases
│   │   ├── __init__.py
│   │   └── test_llm.py         # Pytest suite for API tests
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       └── utils.py            # Utility functions
├── docker-compose.yml          # Docker Compose configuration file
├── Dockerfile-fastapi          # Dockerfile for FastAPI backend
├── Dockerfile-telegram         # Dockerfile for Telegram service
├── frontend/                   # Frontend directory
│   ├── react-frontend/         # React frontend application directory
│   │   ├── public/             # Public directory for static files
│   │   ├── src/                # Source directory
│   │   │   ├── components/     # React components
│   │   │   │   ├── Dashboard.js
│   │   │   │   ├── TaskForm.js
│   │   │   │   ├── TaskList.js
│   │   │   │   ├── ScheduleForm.js
│   │   │   │   ├── ScheduleViewer.js
│   │   │   │   └── fornted.js  # The provided file
│   │   │   ├── services/       # API services
│   │   │   │   ├── api.js
│   │   │   │   └── telegramApi.js
│   │   │   ├── App.js          # Main React component
│   │   │   └── index.js        # Entry point for React application
│   │   ├── .gitignore          # Git ignore file for React frontend
│   │   ├── package.json        # NPM package configuration file
│   │   └── README.md           # README file for React frontend
│   ├── streamlit_app.py        # Streamlit application file
│   └── streamlit_requirements.txt # Streamlit dependencies
├── icon.png                    # Icon image file
├── iconback.png                # Background icon image file
├── README.md                   # Project documentation
├── req.txt                     # Additional requirements file
├── requirements.txt            # Python dependencies
├── run_tests.sh                # Shell script to execute tests
└── test.db                     # SQLite database file for testing
```

- **`main.py`**: Defines API endpoints and contains scheduling logic.
- **`moudles.py`**: Houses SQLAlchemy models and Pydantic schemas for request and response validation.
- **`test_llm.py`**: Contains automated test cases for API functionality.
- **`run_tests.sh`**: A shell script to automate testing.
- **`requirements.txt`**: Lists all required Python dependencies for the project.
- **`Dockerfile-fastapi`**: Contains instructions to containerize the FastAPI backend.
- **`Dockerfile-streamlit`**: Contains instructions to containerize the Streamlit frontend.
- **`Dockerfile-telegram`**: Contains instructions to containerize the Telegram service.
- **`README.md`**: Comprehensive guide to the project.

---

## ⚙️ API Endpoints Overview

| **Method** | **Endpoint**                          | **Description**                                                                                 |
|------------|--------------------------------------|---------------------------------------------------------------------------------------------|
| **POST**   | `/schedule`                          | Generates a task schedule using an LLM or fallback local scheduler.                         |
| **GET**    | `/schedule/{schedule_id}`            | Retrieves a schedule by its unique ID.                                                     |
| **PUT**    | `/schedule/{schedule_id}/task/{task_id}` | Updates a specific task within a schedule.                                                 |

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
   export REDIS_URL="redis://redis:6379/0"
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

## 📜 License

This project is licensed under the [Your License] License. See **LICENSE.md** for details.
```

This `README.md` file provides an overview of the project, its features, prerequisites, setup instructions, project structure, and usage. Adjust the content as needed to fit your specific project details.
This `README.md` file provides an overview of the project, its features, prerequisites, setup instructions, project structure, and usage. Adjust the content as needed to fit your specific project details.