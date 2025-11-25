#!/bin/bash

# 1. Start the Python Resume Engine in the background
# We navigate to the folder and run uvicorn on port 8000
cd /app/resume-engine
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 2. Start the Java Backend in the foreground
# This keeps the container running
cd /app
java -jar app.jar