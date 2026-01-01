#!/bin/bash
# Complete FastAPI service installation script
# Run this ON APP-SERVER (not from Mac)

APP_PATH="/home/vision/bifrost-trader"
SERVICE_NAME="bifrost-api"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo "=========================================="
echo "Installing FastAPI Service"
echo "=========================================="
echo ""

# Check if service file exists in /tmp
if [ ! -f /tmp/bifrost-api.service ]; then
    echo "Creating service file..."
    sudo tee "$SERVICE_FILE" > /dev/null << 'EOF'
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
ExecStart=/home/vision/bifrost-trader/venv/bin/python -m src.main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
else
    echo "Copying service file from /tmp..."
    sudo cp /tmp/bifrost-api.service "$SERVICE_FILE"
fi

# Set permissions
echo "Setting permissions..."
sudo chmod 644 "$SERVICE_FILE"

# Reload systemd
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable service
echo "Enabling service..."
sudo systemctl enable "$SERVICE_NAME"

# Start service
echo "Starting service..."
sudo systemctl start "$SERVICE_NAME"

# Wait a moment
sleep 2

# Check status
echo ""
echo "Service status:"
sudo systemctl status "$SERVICE_NAME" --no-pager | head -20

echo ""
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
echo ""
echo "Service commands:"
echo "  Status:  sudo systemctl status $SERVICE_NAME"
echo "  Start:   sudo systemctl start $SERVICE_NAME"
echo "  Stop:    sudo systemctl stop $SERVICE_NAME"
echo "  Restart: sudo systemctl restart $SERVICE_NAME"
echo "  Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo ""

