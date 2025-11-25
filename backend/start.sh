#!/bin/bash

echo "--- STARTING SERVICES ---"

# 1. Navigate to Resume Engine
cd /app/resume-engine || { echo "ERROR: Could not find /app/resume-engine directory"; exit 1; }

# 2. Start Python in background and log output
echo "--- Launching Python Resume Engine on Port 8000 ---"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /var/log/python_engine.log 2>&1 &

# 3. Wait a few seconds to ensure Python starts
sleep 5

# 4. Check if Python is running
if pgrep -f "uvicorn" > /dev/null; then
    echo "--- Python Engine is RUNNING ---"
else
    echo "--- ERROR: Python Engine FAILED to start ---"
    cat /var/log/python_engine.log
fi

# 5. Start Java Backend
echo "--- Launching Java Backend ---"
cd /app
java -Xmx256m -jar app.jar