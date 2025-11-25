#!/bin/bash

# 1. Start the Python Resume Engine in the background
cd /app/resume-engine
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 2. Start the Java Backend in the foreground (Limited RAM)
cd /app
java -Xmx256m -jar app.jar