# MasterMinutes-FastAPI Task Scheduling API with XAI Integration

This project provides an API for scheduling tasks based on given constraints. It integrates with a Hugging Face language model for task prioritization and uses an XAI (explainable AI) service to assist with task scheduling suggestions.

## Features
- **Task Scheduling**: Schedule tasks based on start and end times, accounting for work hours and breaks.
- **Task Prioritization**: Tasks can be prioritized (high, medium, low).
- **XAI Integration**: Leverages an external XAI service to assist in reordering tasks based on input data.
- **Health Check**: Ensure the model is ready and the server is running.

## Requirements
- Python 3.8 or higher
- `torch`, `transformers`, `fastapi`, `httpx`, and other dependencies (see `requirements.txt`).

## Setup Instructions

### Step 1: Install Dependencies

Clone the repository and install the required Python packages:

```bash
git clone https://github.com/your-repository/task-scheduling-api.git
cd task-scheduling-api
pip install -r requirements.txt


https://github.com/user-attachments/assets/ddb38d8d-ee64-4134-bac9-e480f0cb8c77

