#!/bin/bash

# Kill any existing processes
pkill -f "uvicorn.*:1236" || true
sleep 2

# Start server and wait for startup
python main.py & 
SERVER_PID=$!

# Wait for server to start and model to initialize (up to 5 minutes)
MAX_TRIES=300
count=0

echo "Waiting for server to be ready..."
while [ $count -lt $MAX_TRIES ]; do
    if curl -s http://127.0.0.1:1236/health | grep -q "\"model_ready\":true"; then
        echo "Server is ready!"
        break
    fi
    sleep 1
    count=$((count + 1))
done

if [ $count -eq $MAX_TRIES ]; then
    echo "Server failed to start within timeout"
    kill $SERVER_PID
    exit 1
fi

# Run tests
pytest test_llm.py -v -s

# Cleanup
kill $SERVER_PID