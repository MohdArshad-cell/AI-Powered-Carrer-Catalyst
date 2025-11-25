#!/bin/bash

# 1. Start Python Resume Engine (Background)
cd /app/resume-engine
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 2. Start Java Backend (Foreground)
cd /app
java -Xmx256m -jar app.jar