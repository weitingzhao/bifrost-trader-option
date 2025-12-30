#!/bin/bash
# Deploy to APP-SERVER (10.0.0.80)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SERVER="app-server"
APP_PATH="/opt/bifrost-trader"

echo "=========================================="
echo "Deploying to APP-SERVER (10.0.0.80)"
echo "=========================================="

# Test connection
echo "Testing SSH connection..."
if ! ssh -o ConnectTimeout=5 "$SERVER" "echo 'Connected'" >/dev/null 2>&1; then
    echo "Error: Cannot connect to $SERVER"
    echo "Please run: ./setup-ssh-keys.sh"
    exit 1
fi

# Create directory structure (try with user permissions first)
echo "Creating directory structure..."
ssh "$SERVER" "mkdir -p ~/bifrost-trader || (sudo mkdir -p $APP_PATH && sudo chown \$USER:\$USER $APP_PATH && APP_PATH=$APP_PATH) || APP_PATH=~/bifrost-trader"
APP_PATH="~/bifrost-trader"  # Fallback to home directory

# Sync project files
echo "Syncing project files..."
rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='.env' --exclude='venv' --exclude='.venv' \
    "$PROJECT_ROOT/" "$SERVER:$APP_PATH/"

# Check and install system dependencies
echo "Checking system dependencies..."
ssh "$SERVER" "command -v python3 >/dev/null 2>&1 || echo 'Python3 not found - may need sudo to install'"
ssh "$SERVER" "command -v pip3 >/dev/null 2>&1 || echo 'pip3 not found - may need sudo to install'"

# Install Python dependencies
echo "Installing Python dependencies..."
ssh "$SERVER" "cd $APP_PATH && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

# Create .env file if it doesn't exist
echo "Setting up environment configuration..."
ssh "$SERVER" "cd $APP_PATH && if [ ! -f .env ]; then cat > .env << 'EOF'
IB_HOST=127.0.0.1
IB_PORT=7497
IB_CLIENT_ID=1
DATABASE_URL=postgresql://bifrost:changeme@localhost:5432/options_db
ML_API_URL=http://10.0.0.60:8001
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=False
OPTIONS_CACHE_TTL=60
EOF
fi"

echo "=========================================="
echo "Deployment to APP-SERVER complete!"
echo "Next steps:"
echo "1. Configure PostgreSQL database"
echo "2. Install and configure IB Gateway"
echo "3. Set up systemd services"
echo "=========================================="

