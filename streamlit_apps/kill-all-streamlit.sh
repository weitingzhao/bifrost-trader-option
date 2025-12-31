#!/bin/bash
# Kill all Streamlit processes and free up ports

echo "Killing all Streamlit processes..."

# Kill by process name
pkill -f streamlit
sleep 2

# Kill by ports
for port in 8501 8502 8503 8504 8505 8506 8507 8508 8509 8510; do
    PID=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$PID" ]; then
        echo "Killing process on port $port (PID: $PID)"
        kill -9 $PID 2>/dev/null
    fi
done

sleep 1

# Verify
REMAINING=$(ps aux | grep -i streamlit | grep -v grep | wc -l | tr -d ' ')
if [ "$REMAINING" -eq "0" ]; then
    echo "✅ All Streamlit processes stopped"
    echo "✅ Ports 8501-8510 are now free"
else
    echo "⚠️  Warning: $REMAINING Streamlit process(es) still running:"
    ps aux | grep -i streamlit | grep -v grep
fi

