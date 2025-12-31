#!/bin/bash
# View FastAPI console output from APP-SERVER

SERVER="app-server"
LOG_FILE="/tmp/fastapi.log"
APP_LOG="~/bifrost-trader/app.log"

echo "=========================================="
echo "FastAPI Console Output Viewer"
echo "=========================================="
echo ""

# Check if FastAPI is running
echo "Checking FastAPI status..."
PID=$(ssh "$SERVER" "ps aux | grep 'src.main' | grep -v grep | awk '{print \$2}'" | head -1)

if [ -z "$PID" ]; then
    echo "⚠️  FastAPI is not running"
    exit 1
else
    echo "✅ FastAPI is running (PID: $PID)"
fi

echo ""
echo "Available log sources:"
echo ""

# Check log file
if ssh "$SERVER" "test -f $LOG_FILE"; then
    echo "✅ Log file: $LOG_FILE"
    echo "   Size: $(ssh "$SERVER" "ls -lh $LOG_FILE | awk '{print \$5}'")"
    echo "   Last modified: $(ssh "$SERVER" "stat -c '%y' $LOG_FILE 2>/dev/null || stat -f '%Sm' $LOG_FILE 2>/dev/null")"
else
    echo "❌ Log file not found: $LOG_FILE"
fi

# Check systemd logs
if ssh "$SERVER" "systemctl is-active bifrost-api >/dev/null 2>&1"; then
    echo "✅ Systemd service logs available"
else
    echo "ℹ️  Systemd service not active (using manual process)"
fi

echo ""
echo "=========================================="
echo "View Options:"
echo "=========================================="
echo ""
echo "1. Real-time following (tail -f):"
echo "   ssh $SERVER 'tail -f $LOG_FILE'"
echo ""
echo "2. Last N lines:"
echo "   ssh $SERVER 'tail -50 $LOG_FILE'"
echo ""
echo "3. Systemd logs (if service is active):"
echo "   ssh $SERVER 'sudo journalctl -u bifrost-api -f'"
echo ""
echo "4. All logs with timestamps:"
echo "   ssh $SERVER 'tail -100 $LOG_FILE | grep -E \"INFO|ERROR|WARNING\"'"
echo ""
echo "5. Errors only:"
echo "   ssh $SERVER 'tail -100 $LOG_FILE | grep ERROR'"
echo ""
echo "=========================================="
echo "Quick Commands:"
echo "=========================================="
echo ""
echo "View last 50 lines:"
echo "  ssh $SERVER 'tail -50 $LOG_FILE'"
echo ""
echo "Follow in real-time:"
echo "  ssh $SERVER 'tail -f $LOG_FILE'"
echo ""
echo "Search for errors:"
echo "  ssh $SERVER 'grep -i error $LOG_FILE | tail -20'"
echo ""
echo "View with timestamps:"
echo "  ssh $SERVER 'tail -50 $LOG_FILE'"
echo ""

