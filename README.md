# Task Scheduling API

A FastAPI-based service that generates optimized daily schedules using XAI's Grok model.

## Project Structure
```
.
├── main.py             # FastAPI application and endpoint definitions
├── modules.py          # Data models and schema definitions
├── test_llm.py         # Integration tests for LLM functionality
├── run_tests.sh        # Test runner script
└── README.md           # Project documentation
```

## Features

- Task scheduling with priorities and constraints
- Integration with XAI's Grok model for intelligent scheduling
- Support for breaks and work hours
- CRUD operations for schedules and tasks

## Setup

```bash
# Install dependencies
pip install fastapi uvicorn httpx pydantic pytest

# Set XAI API key
export XAI_API_KEY="your-api-key"

# Run the server
python main.py
```

The server runs at `http://127.0.0.1:1236`

## API Endpoints

### POST /schedule
Creates a new schedule based on tasks and constraints.

Example request:
```json
{
    "tasks": [
        {
            "id": "1",
            "name": "Write report",
            "priority": "high",
            "duration_minutes": 120,
            "deadline": "2024-12-17T12:00:00Z"
        }
    ],
    "constraints": {
        "work_hours_start": "09:00",
        "work_hours_end": "17:00",
        "breaks": [{"start": "12:00", "end": "13:00"}]
    }
}
```

### GET /schedule/{schedule_id}
Retrieves a schedule by ID.

### PUT /schedule/{schedule_id}/task/{task_id}
Updates a specific task in a schedule.

## Testing

```bash
# Run tests
./run_tests.sh
```

## Data Models

### Task
- id: string
- name: string
- priority: "high" | "medium" | "low"
- duration_minutes: integer
- deadline: optional ISO datetime

### Constraints
- work_hours_start: "HH:MM"
- work_hours_end: "HH:MM"
- breaks: array of Break objects