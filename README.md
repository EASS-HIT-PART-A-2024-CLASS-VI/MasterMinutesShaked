# FastAPI Task Scheduling and Model Integration

This repository contains a FastAPI-based application that integrates multiple AI models for task scheduling and natural language processing. The application provides a system that schedules tasks based on user input, using both a Hugging Face model (GPT-2) and an external XAI API for further assistance. The system is designed for managing tasks with various priorities, durations, and deadlines while considering work hours and breaks.

## Features

- **Task Scheduling**: Allows users to input tasks, constraints (work hours and breaks), and receive a schedule based on priorities.
- **AI Model Integration**: Uses Hugging Face (DistilGPT-2) for generating text-based schedules and utilizes an external XAI API for enhanced task prioritization.
- **Health Check**: Provides an endpoint for monitoring the health and readiness of the model.

## Installation

### Prerequisites

- Python 3.7 or higher
- Required libraries: FastAPI, Uvicorn, PyTorch, Hugging Face Transformers, HTTPX, Pydantic, and others.
- Access to an external XAI API (set via environment variable `XAI_API_KEY`).



### Key Points:
-**Setup Instructions**:' git clone https://github.com/your-repository.git
   cd your-repository'
- **Install the dependencies**: `pip install -r requirements.txt`
- **Set environment variables**: Make sure to set the XAI_API_KEY in your environment for the XAI model to function.
  'export XAI_API_KEY="your-api-key-here'
- **Start the application**: `uvicorn main:app --host 127.0.0.1 --port 8000`

## API Endpoints

This section provides details on the available GET and POST requests for the application.

| **Method** | **Endpoint**              | **Description**                                       | **Request Body**                                           | **Response**                                             |
|------------|---------------------------|-------------------------------------------------------|------------------------------------------------------------|----------------------------------------------------------|
| GET        | `/health`                 | Check the health status of the server and model       | None                                                       | JSON object with server and model status.                |
| POST       | `/huggingface/query`      | Query the Hugging Face model with an input prompt     | `{ "input_text": "<prompt>", "max_length": <int> }`        | JSON object with the generated text from the model.      |
| POST       | `/xai/query`              | Query the XAI model with a system prompt and user query | `{ "messages": [{"role": "system", "content": "<prompt>"}, {"role": "user", "content": "<user_query>"}], "model": "<model_name>", "stream": <boolean>, "temperature": <float> }` | JSON object with the model's response to the query.       |
| POST       | `/schedule`               | Schedule tasks based on provided constraints and tasks | `{ "tasks": [ { "id": "<task_id>", "name": "<task_name>", "priority": "<priority>", "duration_minutes": <int>, "deadline": "<deadline>" } ], "constraints": { "work_hours_start": "<HH:MM>", "work_hours_end": "<HH:MM>", "breaks": [ { "start": "<HH:MM>", "end": "<HH:MM>" } ] } }` | JSON object with the scheduled tasks and any notes. |


# API Documentation

This document outlines the available API endpoints and their usage.

## Base URL
`http://127.0.0.1:1236`

## Endpoints

### Health Check
`GET /health`

Checks server and model health status.

**Request**
```bash
curl http://127.0.0.1:1236/health
```

**Response**
```json
{
    "status": "healthy",
    "model_ready": true
}
```

### Query Hugging Face Model
`POST /huggingface/query`

Generate responses using the Hugging Face model.

**Request**
```bash
curl -X POST "http://127.0.0.1:1236/huggingface/query" \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Create a schedule for Elon Musk",
    "max_length": 200
  }'
```

**Response**
```json
{
    "generated_text": "Elon Musk's optimal daily schedule includes gym, meetings, coding, and family time."
}
```

### Query XAI Model
`POST /xai/query`

Generate responses using the XAI model with system prompts.

**Request**
```bash
curl -X POST "http://127.0.0.1:1236/xai/query" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a time management expert."},
      {"role": "user", "content": "Create a daily schedule for me."}
    ],
    "model": "grok-beta",
    "stream": false,
    "temperature": 0.7
  }'
```

**Response**
```json
{
    "choices": [
        {
            "message": {
                "content": "Here's your daily schedule: ...\n"
            }
        }
    ]
}
```

### Schedule Tasks
`POST /schedule`

Create schedules based on tasks and constraints.

**Request Body Parameters**
- `tasks`: Array of tasks with id, name, priority, duration, and deadline
- `constraints`: Work hours and break periods

**Example Request**
```bash
curl -X POST "http://127.0.0.1:1236/schedule" \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {
        "id": "1",
        "name": "Meeting with Team",
        "priority": "high",
        "duration_minutes": 60,
        "deadline": "2024-12-23T09:00:00Z"
      },
      {
        "id": "2",
        "name": "Coding",
        "priority": "medium",
        "duration_minutes": 120,
        "deadline": "2024-12-23T12:00:00Z"
      }
    ],
    "constraints": {
      "work_hours_start": "09:00",
      "work_hours_end": "17:00",
      "breaks": [
        {
          "start": "12:00",
          "end": "13:00"
        }
      ]
    }
  }'
```

**Response**
```json
{
    "schedule": [
        {
            "task_id": "1",
            "start_time": "09:00",
            "end_time": "10:00"
        },
        {
            "task_id": "2",
            "start_time": "13:00",
            "end_time": "15:00"
        }
    ],
    "notes": "Tasks scheduled successfully within the work hours."
}
```


