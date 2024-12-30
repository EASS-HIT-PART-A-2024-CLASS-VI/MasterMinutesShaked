# 📅 AI-Powered Task Scheduler

FastAPI application integrating multiple AI models (Grok and HuggingFace GPT-2) for intelligent task scheduling and natural language processing.

## 🎯 Features

* **🤖 Dual AI Integration**: HuggingFace (DistilGPT-2) for text generation + Grok for task prioritization
* **⚡ Smart Scheduling**: Priority-based task arrangement with constraints
* **🕒 Time Management**: Work hours and breaks handling
* **🔍 Health Monitoring**: Real-time system and model status checks

## 🛠️ Technologies

* **🚀 FastAPI & Uvicorn**: Web framework and ASGI server
* **🤖 AI Models**: Grok API and HuggingFace Transformers
* **🐍 PyTorch**: Deep learning framework
* **✨ Pydantic & HTTPX**: Data validation and HTTP client

## 📂 Project Structure
```
.
├── main.py           # FastAPI app and endpoints
├── modules.py        # Data models and schemas
├── test_llm.py       # LLM integration tests
├── run_tests.sh      # Test runner script
└── README.md         # Documentation
```

## 📥 Installation

### Prerequisites
```bash
Python 3.7+
pip install fastapi uvicorn pytorch transformers httpx pydantic pytest
export XAI_API_KEY="your-key"
```

### Quick Start
```bash
git clone https://github.com/yourusername/task-scheduler.git
cd task-scheduler
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 1236
```

[Previous sections remain the same until API Reference]

## 🚀 API Reference

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|-----------|
| GET | `/health` | Health check | None | `{"status": "healthy", "model_ready": true}` |
| GET | `/schedule/{schedule_id}` | Fetch schedule | None | Schedule details with tasks |
| POST | `/schedule` | Create schedule | `{"tasks": [{"id": str, "name": str, "priority": str, "duration_minutes": int}], "constraints": {"work_hours_start": "HH:MM", "work_hours_end": "HH:MM"}}` | Generated schedule with ID |
| PUT | `/schedule/{schedule_id}/task/{task_id}` | Update task | `{"task_id": str, "start_time": "HH:MM", "end_time": "HH:MM"}` | Updated task schedule |
| POST | `/xai/query` | Query Grok model | `{"messages": [], "model": "grok-beta", "stream": false, "temperature": float}` | AI model response |

[Rest of the README remains the same]
### Example: Create Schedule
```bash
curl -X POST "http://localhost:1236/schedule" \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {
        "id": "1",
        "name": "Team Meeting",
        "priority": "high",
        "duration_minutes": 60,
        "deadline": "2024-12-23T09:00:00Z"
      }
    ],
    "constraints": {
      "work_hours_start": "09:00",
      "work_hours_end": "17:00",
      "breaks": [{"start": "12:00", "end": "13:00"}]
    }
  }'
```

### Response Format
```json
{
    "schedule": [
        {
            "task_id": "1",
            "start_time": "09:00",
            "end_time": "10:00"
        }
    ],
    "notes": "Tasks scheduled successfully within work hours."
}
```

## 🧪 Testing
```bash
./run_tests.sh
```

## 📚 Documentation
Access full API documentation at: `http://localhost:1236/docs`

