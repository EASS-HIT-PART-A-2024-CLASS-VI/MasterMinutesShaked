#!/bin/bash

# Exit on first error
set -e

# Base URL of the FastAPI application
BASE_URL="http://127.0.0.1:8000"

# Function to test the /schedule endpoint
test_schedule_endpoint() {
  echo "Testing /schedule endpoint..."
  INPUT_DATA=$(cat <<EOF
{
  "tasks": [
    {"id": "1", "name": "Write report", "priority": "high", "duration_minutes": 120, "deadline": "2024-12-17T12:00:00Z"},
    {"id": "2", "name": "Team meeting", "priority": "medium", "duration_minutes": 60, "deadline": null}
  ],
  "constraints": {
    "work_hours_start": "09:00",
    "work_hours_end": "17:00",
    "breaks": [{"start": "12:00", "end": "13:00"}]
  }
}
EOF
)

  RESPONSE=$(curl -s -X POST "$BASE_URL/schedule" \
    -H "Content-Type: application/json" \
    -d "$INPUT_DATA")

  echo "Response: $RESPONSE"
}

# Function to test the /schedule/{schedule_id}/task/{task_id} endpoint
test_update_task_endpoint() {
  echo "Testing /schedule/{schedule_id}/task/{task_id} endpoint..."
  
  SCHEDULE_ID="some-unique-id"  # Replace with a valid schedule_id from a previous response
  TASK_ID="1"                  # Replace with a valid task_id from the schedule
  
  UPDATED_TASK=$(cat <<EOF
{
  "task_id": "$TASK_ID",
  "start_time": "10:00",
  "end_time": "12:00",
  "name": "Write updated report"
}
EOF
)

  RESPONSE=$(curl -s -X PUT "$BASE_URL/schedule/$SCHEDULE_ID/task/$TASK_ID" \
    -H "Content-Type: application/json" \
    -d "$UPDATED_TASK")

  echo "Response: $RESPONSE"
}

# Function to test the /schedule/{schedule_id} endpoint
test_get_schedule_endpoint() {
  echo "Testing /schedule/{schedule_id} endpoint..."
  
  SCHEDULE_ID="some-unique-id"  # Replace with a valid schedule_id from a previous response
  
  RESPONSE=$(curl -s -X GET "$BASE_URL/schedule/$SCHEDULE_ID")

  echo "Response: $RESPONSE"
}

# Function to test the /xai/query endpoint
test_query_xai_model_endpoint() {
  echo "Testing /xai/query endpoint..."
  
  QUERY_DATA=$(cat <<EOF
{
  "messages": [
    {"role": "system", "content": "Test scheduling assistant query."},
    {"role": "user", "content": "What is the best way to organize tasks for the day?"}
  ],
  "model": "grok-beta",
  "stream": false,
  "temperature": 0.5
}
EOF
)

  RESPONSE=$(curl -s -X POST "$BASE_URL/xai/query" \
    -H "Content-Type: application/json" \
    -d "$QUERY_DATA")

  echo "Response: $RESPONSE"
}

# Run tests
test_schedule_endpoint
test_update_task_endpoint
test_get_schedule_endpoint
test_query_xai_model_endpoint

echo "All tests completed successfully!"
