# Manual FastAPI Service Setup on APP-SERVER

Since sudo access is required, follow these steps manually on APP-SERVER.

## Option 1: Run Setup Script on Server

```bash
# Copy the setup script to server
scp scripts/management/setup-fastapi-service-remote.sh app-server:/tmp/

# SSH to server and run
ssh app-server
bash /tmp/setup-fastapi-service-remote.sh
```

## Option 2: Manual Setup

### Step 1: SSH to APP-SERVER

```bash
ssh app-server
```

### Step 2: Create Systemd Service File

```bash
sudo nano /etc/systemd/system/bifrost-api.service
```

Paste the following content:

```ini
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
```

Save and exit (Ctrl+X, then Y, then Enter).

### Step 3: Set Permissions

```bash
sudo chmod 644 /etc/systemd/system/bifrost-api.service
```

### Step 4: Reload Systemd

```bash
sudo systemctl daemon-reload
```

### Step 5: Enable Service (Start on Boot)

```bash
sudo systemctl enable bifrost-api
```

### Step 6: Start Service

```bash
sudo systemctl start bifrost-api
```

### Step 7: Check Status

```bash
sudo systemctl status bifrost-api
```

You should see "active (running)" status.

### Step 8: View Logs (if needed)

```bash
# Follow logs in real-time
sudo journalctl -u bifrost-api -f

# View last 50 lines
sudo journalctl -u bifrost-api -n 50
```

## Verify Service is Running

From your Mac, test the API:

```bash
# Health check
curl http://10.0.0.80:8000/api/health

# Or check from server
ssh app-server "curl http://localhost:8000/api/health"
```

## Service Management Commands

```bash
# Check status
sudo systemctl status bifrost-api

# Start service
sudo systemctl start bifrost-api

# Stop service
sudo systemctl stop bifrost-api

# Restart service
sudo systemctl restart bifrost-api

# View logs
sudo journalctl -u bifrost-api -f

# Disable auto-start
sudo systemctl disable bifrost-api
```

## Troubleshooting

### Service Fails to Start

1. Check logs:
   ```bash
   sudo journalctl -u bifrost-api -n 100
   ```

2. Verify Python path:
   ```bash
   ls -la /home/vision/bifrost-trader/venv/bin/python
   ```

3. Test manually:
   ```bash
   cd /home/vision/bifrost-trader
   source venv/bin/activate
   python -m src.main
   ```

### Port Already in Use

If port 8000 is already in use:

```bash
# Find what's using the port
sudo lsof -i :8000

# Or check if another instance is running
ps aux | grep "src.main"
```

### Permission Issues

Make sure the service file has correct ownership:

```bash
sudo chown root:root /etc/systemd/system/bifrost-api.service
sudo chmod 644 /etc/systemd/system/bifrost-api.service
```

