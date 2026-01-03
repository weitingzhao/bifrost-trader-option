#!/bin/bash
# Check setup status on APP-SERVER

SERVER="app-server"
echo "=========================================="
echo "Checking APP-SERVER (10.0.0.80) Setup"
echo "=========================================="
echo ""

# Check SSH connection
echo "1. SSH Connection:"
if ssh -o ConnectTimeout=5 "$SERVER" "echo 'OK'" >/dev/null 2>&1; then
    echo "   ✓ Connected"
else
    echo "   ✗ Cannot connect"
    exit 1
fi

# Check Python
echo ""
echo "2. Python Installation:"
PYTHON_VERSION=$(ssh "$SERVER" "python3 --version 2>&1")
if [ $? -eq 0 ]; then
    echo "   ✓ $PYTHON_VERSION"
else
    echo "   ✗ Python3 not found"
fi

# Check pip
echo ""
echo "3. pip Installation:"
PIP_VERSION=$(ssh "$SERVER" "python3 -m pip --version 2>&1")
if [ $? -eq 0 ]; then
    echo "   ✓ $PIP_VERSION"
else
    echo "   ✗ pip not found"
fi

# Check venv
echo ""
echo "4. Virtual Environment:"
if ssh "$SERVER" "cd ~/bifrost-trader && test -d venv && echo 'exists'" >/dev/null 2>&1; then
    echo "   ✓ Virtual environment exists"
    PACKAGE_COUNT=$(ssh "$SERVER" "cd ~/bifrost-trader && source venv/bin/activate && pip list 2>/dev/null | wc -l")
    echo "   ✓ Installed packages: $PACKAGE_COUNT"
else
    echo "   ✗ Virtual environment not created"
fi

# Check PostgreSQL
echo ""
echo "5. PostgreSQL:"
PG_STATUS=$(ssh "$SERVER" "systemctl is-active postgresql 2>/dev/null || echo 'not_active'")
if [ "$PG_STATUS" = "active" ]; then
    echo "   ✓ PostgreSQL is running"
    PG_VERSION=$(ssh "$SERVER" "psql --version 2>/dev/null || echo 'version_unknown'")
    echo "   $PG_VERSION"
else
    echo "   ✗ PostgreSQL not running or not installed"
fi

# Check project files
echo ""
echo "6. Project Files:"
if ssh "$SERVER" "cd ~/bifrost-trader && test -f app_fastapi/api/main.py && echo 'exists'" >/dev/null 2>&1; then
    echo "   ✓ Code is deployed"
    FILE_COUNT=$(ssh "$SERVER" "cd ~/bifrost-trader && find src -name '*.py' | wc -l")
    echo "   ✓ Python files: $FILE_COUNT"
else
    echo "   ✗ Code not found"
fi

# Check .env file
echo ""
echo "7. Configuration:"
if ssh "$SERVER" "cd ~/bifrost-trader && test -f .env && echo 'exists'" >/dev/null 2>&1; then
    echo "   ✓ .env file exists"
else
    echo "   ⚠ .env file not found (needs to be created)"
fi

# Check systemd service
echo ""
echo "8. FastAPI Service:"
SERVICE_STATUS=$(ssh "$SERVER" "systemctl is-active bifrost-api 2>/dev/null || echo 'not_installed'")
if [ "$SERVICE_STATUS" = "active" ]; then
    echo "   ✓ FastAPI service is running"
elif [ "$SERVICE_STATUS" = "inactive" ]; then
    echo "   ⚠ FastAPI service exists but is not running"
else
    echo "   ⚠ FastAPI service not configured"
fi

echo ""
echo "=========================================="
echo "Setup Check Complete"
echo "=========================================="

