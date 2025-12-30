#!/bin/bash
# Start the status monitor web GUI

cd "$(dirname "$0")"
echo "Starting Bifrost Status Monitor..."
echo "Access the dashboard at: http://localhost:5000"
echo ""
python3 app.py

