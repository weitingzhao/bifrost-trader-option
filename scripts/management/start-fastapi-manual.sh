#!/bin/bash
# Start FastAPI manually (without systemd) - temporary solution

SERVER="app-server"

echo "Starting FastAPI manually on APP-SERVER..."

# Check if already running
if ssh "$SERVER" "ps aux | grep 'src.main' | grep -v grep" >/dev/null 2>&1; then
    echo "FastAPI is already running!"
    exit 0
fi

# Start FastAPI in background
ssh "$SERVER" "cd ~/bifrost-trader && source venv/bin/activate && nohup python -m src.main > /tmp/fastapi.log 2>&1 &"

sleep 2

# Check if started
if ssh "$SERVER" "ps aux | grep 'src.main' | grep -v grep" >/dev/null 2>&1; then
    echo "✓ FastAPI started successfully!"
    echo ""
    echo "Check status:"
    ssh "$SERVER" "ps aux | grep 'src.main' | grep -v grep"
    echo ""
    echo "View logs: ssh app-server 'tail -f /tmp/fastapi.log'"
    echo "Stop: ssh app-server \"pkill -f 'src.main'\""
else
    echo "✗ Failed to start FastAPI"
    echo "Check logs: ssh app-server 'cat /tmp/fastapi.log'"
fi

