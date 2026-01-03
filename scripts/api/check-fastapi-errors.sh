#!/bin/bash
# Check FastAPI service errors and status

SERVER="app-server"
APP_PATH="/home/vision/bifrost-trader"

echo "=========================================="
echo "FastAPI Service Diagnostic"
echo "=========================================="
echo ""

# Check if service file exists
echo "1. Service File:"
if ssh "$SERVER" "test -f /etc/systemd/system/bifrost-api.service"; then
    echo "   ✓ Service file exists"
    ssh "$SERVER" "sudo systemctl status bifrost-api --no-pager 2>&1 | head -10" || echo "   ⚠ Cannot check status (needs sudo)"
else
    echo "   ✗ Service file NOT found"
    echo "   → Service needs to be set up"
fi

echo ""
echo "2. Code Check:"
if ssh "$SERVER" "cd $APP_PATH && test -f app_fastapi/api/main.py"; then
    echo "   ✓ Code is deployed"
else
    echo "   ✗ Code not found"
fi

echo ""
echo "3. Virtual Environment:"
if ssh "$SERVER" "cd $APP_PATH && test -d venv"; then
    echo "   ✓ Virtual environment exists"
    PACKAGE_COUNT=$(ssh "$SERVER" "cd $APP_PATH && source venv/bin/activate && pip list 2>/dev/null | wc -l")
    echo "   ✓ Packages installed: $PACKAGE_COUNT"
else
    echo "   ✗ Virtual environment not found"
fi

echo ""
echo "4. Python Import Test:"
IMPORT_TEST=$(ssh "$SERVER" "cd $APP_PATH && source venv/bin/activate && python -c 'from app_fastapi.api.main import app' 2>&1")
if [ $? -eq 0 ]; then
    echo "   ✓ Code imports successfully"
else
    echo "   ✗ Import failed:"
    echo "   $IMPORT_TEST"
fi

echo ""
echo "5. Manual Start Test:"
echo "   Testing if FastAPI can start manually..."
MANUAL_TEST=$(ssh "$SERVER" "cd $APP_PATH && source venv/bin/activate && timeout 3 uvicorn app_fastapi.api.main:app --host 0.0.0.0 --port 8000 2>&1" | head -10)
if echo "$MANUAL_TEST" | grep -q "Application startup\|Uvicorn running\|Started server"; then
    echo "   ✓ FastAPI can start"
else
    echo "   ⚠ FastAPI startup test:"
    echo "   $MANUAL_TEST"
fi

echo ""
echo "6. Port Check:"
PORT_CHECK=$(ssh "$SERVER" "netstat -tlnp 2>/dev/null | grep :8000 || ss -tlnp 2>/dev/null | grep :8000 || echo 'Port 8000 not in use'")
echo "   $PORT_CHECK"

echo ""
echo "=========================================="
echo "Summary:"
echo "=========================================="
echo ""
if ssh "$SERVER" "test -f /etc/systemd/system/bifrost-api.service"; then
    echo "Service file exists but may not be running."
    echo "To start: ssh $SERVER 'sudo systemctl start bifrost-api'"
else
    echo "Service file does NOT exist."
    echo "To set up:"
    echo "  1. ssh $SERVER"
    echo "  2. bash /tmp/setup-fastapi.sh"
    echo ""
    echo "Or see: scripts/management/setup-fastapi-manual.md"
fi
echo ""

