#!/bin/bash
# Script to run ON APP-SERVER to set up FastAPI service
# Run this script on APP-SERVER: ssh app-server 'bash -s' < setup-fastapi-service-remote.sh

APP_PATH="/home/vision/bifrost-trader"
SERVICE_NAME="bifrost-api"

echo "Setting up FastAPI service..."

# Create systemd service file
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << 'EOF'
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

# Set permissions
sudo chmod 644 /etc/systemd/system/$SERVICE_NAME.service

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable $SERVICE_NAME

# Start service
sudo systemctl start $SERVICE_NAME

# Wait a moment
sleep 2

# Check status
echo ""
echo "Service status:"
sudo systemctl status $SERVICE_NAME --no-pager | head -15

echo ""
echo "Service setup complete!"
echo ""
echo "Useful commands:"
echo "  Check status:  sudo systemctl status $SERVICE_NAME"
echo "  Start service: sudo systemctl start $SERVICE_NAME"
echo "  Stop service:   sudo systemctl stop $SERVICE_NAME"
echo "  Restart:       sudo systemctl restart $SERVICE_NAME"
echo "  View logs:     sudo journalctl -u $SERVICE_NAME -f"
echo "  View recent:   sudo journalctl -u $SERVICE_NAME -n 50"

