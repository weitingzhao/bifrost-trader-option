#!/bin/bash
# Restart Streamlit to see the new FastAPI Live Logs menu

echo "=========================================="
echo "Restarting Streamlit Monitor"
echo "=========================================="
echo ""

# Kill existing Streamlit processes
echo "Stopping existing Streamlit processes..."
pkill -f streamlit
sleep 2

# Check if killed
REMAINING=$(ps aux | grep -i streamlit | grep -v grep | wc -l | tr -d ' ')
if [ "$REMAINING" -eq "0" ]; then
    echo "✅ All Streamlit processes stopped"
else
    echo "⚠️  Some processes still running, forcing kill..."
    pkill -9 -f streamlit
    sleep 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Verify pages directory exists
if [ -d "pages" ]; then
    echo "✅ Pages directory found"
    echo "Pages available:"
    ls -1 pages/ 2>/dev/null | sed 's/^/   - /'
else
    echo "⚠️  Pages directory not found!"
    exit 1
fi

echo ""
echo "Starting Streamlit..."
echo "Location: $SCRIPT_DIR"
echo ""

# Start Streamlit
streamlit run app.py

echo ""
echo "Streamlit started!"
echo "Open: http://localhost:8501"
echo ""
echo "Look in the SIDEBAR for:"
echo "  📊 Bifrost APP-SERVER Monitor"
echo "  📝 FastAPI Live Logs"

