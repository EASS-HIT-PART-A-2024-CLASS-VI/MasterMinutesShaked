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

### Example: `/health` GET request
- **Request:**
  ```bash
  curl http://127.0.0.1:1236/health
  5. POST /schedule (With additional task)
Description: Example of scheduling additional tasks while respecting work hour constraints.


