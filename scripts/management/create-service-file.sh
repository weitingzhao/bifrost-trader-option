#!/bin/bash
# Create systemd service file on APP-SERVER

SERVER="app-server"
SERVICE_FILE="/tmp/bifrost-api.service"

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
ExecStart=/home/vision/bifrost-trader/venv/bin/python -m src.main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "Copying service file to server..."
scp "$SERVICE_FILE" "$SERVER:/tmp/bifrost-api.service"

echo ""
echo "Service file created and copied to server."
echo ""
echo "Now run these commands on APP-SERVER:"
echo "  ssh app-server"
echo "  sudo mv /tmp/bifrost-api.service /etc/systemd/system/"
echo "  sudo chmod 644 /etc/systemd/system/bifrost-api.service"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable bifrost-api"
echo "  sudo systemctl start bifrost-api"
echo "  sudo systemctl status bifrost-api"
echo ""

