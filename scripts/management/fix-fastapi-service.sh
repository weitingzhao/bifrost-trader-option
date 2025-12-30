#!/bin/bash
# Complete fix for FastAPI service - run this from Mac
# It will guide you through the setup

SERVER="app-server"

echo "=========================================="
echo "FastAPI Service Fix"
echo "=========================================="
echo ""

# Check current status
echo "1. Checking current status..."
SERVICE_STATUS=$(ssh "$SERVER" "systemctl is-active bifrost-api 2>/dev/null || echo 'not_active'")
echo "   Service status: $SERVICE_STATUS"

if [ "$SERVICE_STATUS" = "active" ]; then
    echo "   ✓ Service is already running!"
    exit 0
fi

# Check if service file exists
echo ""
echo "2. Checking service file..."
if ssh "$SERVER" "test -f /etc/systemd/system/bifrost-api.service"; then
    echo "   ✓ Service file exists"
else
    echo "   ✗ Service file missing - will create it"
fi

# Check if code is ready
echo ""
echo "3. Verifying code..."
if ssh "$SERVER" "cd ~/bifrost-trader && test -f src/main.py && test -d venv"; then
    echo "   ✓ Code and venv ready"
else
    echo "   ✗ Code or venv missing"
    exit 1
fi

# Test manual start
echo ""
echo "4. Testing manual start..."
MANUAL_TEST=$(ssh "$SERVER" "cd ~/bifrost-trader && source venv/bin/activate && timeout 2 python -m src.main 2>&1" | grep -i "uvicorn\|started\|running" | head -3)
if [ -n "$MANUAL_TEST" ]; then
    echo "   ✓ FastAPI can start: $MANUAL_TEST"
else
    echo "   ⚠ Manual start test inconclusive"
fi

echo ""
echo "=========================================="
echo "Installation Required"
echo "=========================================="
echo ""
echo "The service file needs to be installed with sudo."
echo ""
echo "Run this command (will ask for sudo password once):"
echo ""
echo "  ssh -t app-server 'bash /tmp/install-service.sh'"
echo ""
echo "Or manually:"
echo "  1. ssh app-server"
echo "  2. bash /tmp/install-service.sh"
echo ""
echo "After installation, verify with:"
echo "  ssh app-server 'sudo systemctl status bifrost-api'"
echo ""

