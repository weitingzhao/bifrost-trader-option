#!/bin/bash
# Kill all Streamlit processes and start only the monitoring app

echo "=========================================="
echo "Streamlit Cleanup and Restart"
echo "=========================================="
echo ""

# Find all Streamlit processes
echo "Finding Streamlit processes..."
STREAMLIT_PIDS=$(ps aux | grep -i streamlit | grep -v grep | awk '{print $2}')

if [ -z "$STREAMLIT_PIDS" ]; then
    echo "✅ No Streamlit processes found"
else
    echo "Found Streamlit PIDs: $STREAMLIT_PIDS"
    echo "Killing all Streamlit processes..."
    pkill -f streamlit
    sleep 2
    echo "✅ Killed all Streamlit processes"
fi

# Free up common Streamlit ports
echo ""
echo "Freeing up ports 8501-8505..."
for port in 8501 8502 8503 8504 8505; do
    PID=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$PID" ]; then
        echo "Killing process on port $port (PID: $PID)"
        kill -9 $PID 2>/dev/null
    fi
done
sleep 1

# Verify cleanup
REMAINING=$(ps aux | grep -i streamlit | grep -v grep | wc -l | tr -d ' ')
if [ "$REMAINING" -eq "0" ]; then
    echo "✅ All Streamlit processes stopped"
else
    echo "⚠️  Warning: $REMAINING Streamlit process(es) still running"
    ps aux | grep -i streamlit | grep -v grep
fi

echo ""
echo "=========================================="
echo "Starting Single Streamlit Instance"
echo "=========================================="
echo ""

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Start the monitoring app
echo "Starting Streamlit monitoring app..."
echo "Location: $SCRIPT_DIR"
echo ""

streamlit run app.py

echo ""
echo "Streamlit monitor started!"
echo "Access at: http://localhost:8501"

