#!/bin/bash
# Set up FastAPI service on APP-SERVER

set -e

SERVER="app-server"
APP_PATH="/home/vision/bifrost-trader"
SERVICE_NAME="bifrost-api"
SERVICE_FILE="/tmp/bifrost-api.service"

echo "=========================================="
echo "Setting up FastAPI service on APP-SERVER"
echo "=========================================="
echo ""

# Test connection
echo "Testing SSH connection..."
if ! ssh -o ConnectTimeout=5 "$SERVER" "echo 'Connected'" >/dev/null 2>&1; then
    echo "Error: Cannot connect to $SERVER"
    exit 1
fi

# Create systemd service file
echo "Creating systemd service file..."
cat > "$SERVICE_FILE" << 'EOF'
[Unit]
Description=Bifrost Options Trading API
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=vision
Group=vision
WorkingDirectory=/home/vision/bifrost-trader
Environment="PATH=/home/vision/bifrost-trader/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/home/vision/bifrost-trader/venv/bin/uvicorn app_fastapi.api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Copy service file to server
echo "Copying service file to server..."
scp "$SERVICE_FILE" "$SERVER:/tmp/$SERVICE_NAME.service"

# Install service
echo "Installing systemd service..."
ssh "$SERVER" "sudo mv /tmp/$SERVICE_NAME.service /etc/systemd/system/$SERVICE_NAME.service && sudo chmod 644 /etc/systemd/system/$SERVICE_NAME.service"

# Reload systemd
echo "Reloading systemd daemon..."
ssh "$SERVER" "sudo systemctl daemon-reload"

# Enable service
echo "Enabling service to start on boot..."
ssh "$SERVER" "sudo systemctl enable $SERVICE_NAME"

# Start service
echo "Starting FastAPI service..."
ssh "$SERVER" "sudo systemctl start $SERVICE_NAME"

# Wait a moment
sleep 2

# Check status
echo ""
echo "Checking service status..."
ssh "$SERVER" "sudo systemctl status $SERVICE_NAME --no-pager | head -15"

echo ""
echo "=========================================="
echo "FastAPI service setup complete!"
echo "=========================================="
echo ""
echo "Service commands:"
echo "  Check status:  ssh $SERVER 'sudo systemctl status $SERVICE_NAME'"
echo "  Start service: ssh $SERVER 'sudo systemctl start $SERVICE_NAME'"
echo "  Stop service:  ssh $SERVER 'sudo systemctl stop $SERVICE_NAME'"
echo "  View logs:     ssh $SERVER 'sudo journalctl -u $SERVICE_NAME -f'"
echo ""

