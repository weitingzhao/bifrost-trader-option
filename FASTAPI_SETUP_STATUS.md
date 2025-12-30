# FastAPI Service Setup Status

## Current Status

✅ **Code**: Deployed and working  
✅ **Virtual Environment**: Created with all packages  
✅ **Manual Start**: FastAPI can start successfully  
✅ **Configuration**: .env file exists  
❌ **Systemd Service**: NOT set up yet (requires sudo)

## Diagnosis

The FastAPI application code is working correctly. When tested manually, it starts successfully:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The issue is that the **systemd service file doesn't exist yet** because it requires sudo access to create.

## Solution: Set Up Systemd Service

### Quick Setup (Recommended)

1. **SSH to APP-SERVER**:
   ```bash
   ssh app-server
   ```

2. **Run the setup script** (requires sudo password):
   ```bash
   bash /tmp/setup-fastapi.sh
   ```

3. **Verify service is running**:
   ```bash
   sudo systemctl status bifrost-api
   ```

### Manual Setup

If the script doesn't work, follow these steps:

1. **SSH to APP-SERVER**:
   ```bash
   ssh app-server
   ```

2. **Create service file**:
   ```bash
   sudo nano /etc/systemd/system/bifrost-api.service
   ```

3. **Paste this content**:
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

4. **Save and exit** (Ctrl+X, Y, Enter)

5. **Set permissions**:
   ```bash
   sudo chmod 644 /etc/systemd/system/bifrost-api.service
   ```

6. **Reload and enable**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable bifrost-api
   sudo systemctl start bifrost-api
   ```

7. **Check status**:
   ```bash
   sudo systemctl status bifrost-api
   ```

## Verify Service is Running

After setup, verify from your Mac:

```bash
# Check service status
ssh app-server "sudo systemctl status bifrost-api"

# Test API endpoint
curl http://10.0.0.80:8000/api/health

# Or from server
ssh app-server "curl http://localhost:8000/api/health"
```

## Expected Result

Once the service is running, you should see:

- ✅ Service status: `active (running)`
- ✅ API responds: `{"status": "healthy"}` or similar
- ✅ Streamlit monitor shows: FastAPI status = "running"

## Troubleshooting

### If Service Fails to Start

Check logs:
```bash
ssh app-server "sudo journalctl -u bifrost-api -n 50"
```

Common issues:
- **IB Gateway not running**: Service will start but API calls to IB will fail (expected until IB Gateway is set up)
- **Port 8000 in use**: Check with `sudo lsof -i :8000`
- **Python path wrong**: Verify `ls -la /home/vision/bifrost-trader/venv/bin/python`

### Test Manually First

Before setting up service, test manually:
```bash
ssh app-server
cd ~/bifrost-trader
source venv/bin/activate
python -m src.main
```

If this works, the service should work too.

## Next Steps

1. Set up the systemd service (follow steps above)
2. Verify service is running
3. The Streamlit monitor will automatically detect it
4. When IB Gateway is approved, configure IB connection

