
# 📅MasterMinutes: A LLM-Powered Task Scheduler Application
MasterMinutes is an AI-powered Pomodoro-based task scheduling application that helps you stay focused and productive. Leveraging advanced LLM capabilities, it intelligently organizes your tasks, optimizes work sessions, and provides smart recommendations to enhance time management. Whether you're tackling deep work, managing multiple projects, or simply aiming to boost efficiency, MasterMinutes ensures you make the most of every minute.
---


## 🎥 Youtube link:

[https://www.youtube.com/watch?v=iYtngpLOuL0&ab_channel=ShakedNuttman](https://www.youtube.com/watch?v=mz9wgAVuZhU&ab_channel=ShakedNuttman)
## 📊 System Design Overview

Below is a high-level system design that illustrates how **MasterMinutes** components interact with each other. Each sub-component is explained in terms of its role and why it is needed.

![Project Diagram](./diagram.png)

1. **MasterMinutes Web App (React)**  
   - **Role**: A React-based frontend interface.  
   - **Purpose**: Provides a user-friendly platform to manage tasks, view schedules, and monitor Pomodoro sessions in real-time.  
   - **Why Needed**: Ensures a responsive and interactive experience, making it simple to handle tasks and track productivity.

2. **Telegram Sync and Reminder Service**  
   - **Role**: A backend service responsible for scheduling and sending reminders.  
   - **Purpose**: Integrates with Telegram to push notifications and reminders, ensuring users stay updated on tasks and timers.  
   - **Why Needed**: Offers an alternative notification channel beyond the web app, improving accessibility and user engagement.

3. **MasterMinutes API (FastAPI)**  
   - **Role**: The main backend API for the application.  
   - **Purpose**: Handles core logic for task management, scheduling, and user data. It exposes endpoints for the React frontend and the Telegram service.  
   - **Why Needed**: Centralizes business logic and data flow, ensuring consistent operations and easy maintenance.

4. **Google Gemini (LLM)**  
   - **Role**: The AI/LLM component integrated into the system.  
   - **Purpose**: Provides intelligent recommendations, such as optimal Pomodoro durations, task ordering, and productivity tips.  
   - **Why Needed**: Elevates the user experience by offering context-aware assistance, saving time, and improving efficiency.

5. **Cache (Redis)**  
   - **Role**: A caching layer for frequently accessed or transient data.  
   - **Purpose**: Stores session data, scheduling info, and other data that benefit from quick retrieval.  
   - **Why Needed**: Enhances performance and scalability by reducing the load on the primary data store and speeding up data access.

6. **Telegram (Cloud/External Services)**  
   - **Role**: External messaging platform used for notifications.  
   - **Purpose**: Delivers reminders and updates to users directly via Telegram messages.  
   - **Why Needed**: Expands the ways users can interact with MasterMinutes, making sure they never miss an important reminder.

---

### How It All Fits Together

1. **User Interaction**: The user works within the **MasterMinutes Web App (React)** to create tasks, set Pomodoro timers, and manage schedules.  
2. **API Requests**: The React frontend communicates with the **MasterMinutes API (FastAPI)** for all core functionalities.  
3. **AI Recommendations**: When smart suggestions are needed, the API consults **Gpt4All** to generate optimal task orders or productivity tips.  
4. **Caching**: Data that needs to be quickly accessed (e.g., user session info) is stored in **Redis**, improving performance and reducing repetitive database calls.  
5. **Notifications**: The **Telegram Sync and Reminder Service** schedules and sends reminders to users via **Telegram**, ensuring timely updates and higher engagement.  

By separating concerns across these distinct components, **MasterMinutes** remains modular, scalable, and maintainable—ready to help you make the most of every minute.






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
   Create .env file in backend folder, react folder and root folder which contain the following variables 

   ```bash
   
   GOOGLE_API_KEY="your_gemini_api_key"
   REDIS_URL="your_redis_url"
   TELEGRAM_TOKEN="your_telegram_bot_token"
   TELEGRAM_CHAT_ID="your_telegram_chat_id"
   ```

6. **Run the application:**
   ```bash
   uvicorn main:app --port 1236 --reload
   ```

7. **Run tests:**
   You need to run the docker containers (Use the "Running with docker-compose" below).
   Then open a new termial instance in the project's root folder run the following command:
   ```bash
   pytest backend/tests/test_llm.py
   ```

9. **Access the API Docs:**
   Navigate to **[http://127.0.0.1:1236/docs](http://127.0.0.1:1236/docs)** for Swagger UI.

---

## 🐳 Running with docker-compose

1. **Build the Docker images:**
   ```bash
   docker-compose build  
   ```

2. **Run the containers:**
   ```bash
   docker-compose up
   ```

3. **Access the API Docs:**
   Visit **[http://127.0.0.1:1236/docs](http://127.0.0.1:1236/docs)**.

   
4. **Access the Web Application:**
   Visit **[http://127.0.0.1:3000](http://127.0.0.1:3000)**.

---

## 🧪 Running Tests

To validate the functionality:
```bash
pytest backend/tests/test_llm.py
```
This script:
- Starts the application.
- Runs all test cases.
- Shuts down the application.

---
