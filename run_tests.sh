#!/bin/bash

# Start the FastAPI application in the background
uvicorn main:app --port 1236 --reload &
APP_PID=$!

# Wait for the application to start (give it some time)
sleep 5

# Run the tests using pytest
pytest test_llm.py

# Stop the FastAPI application
kill $APP_PID

echo "Tests completed."