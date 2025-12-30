# Status Monitor Guide

## Overview

A web-based status monitoring dashboard has been created to monitor APP-SERVER (10.0.0.80) from your Mac.

## Location

- **Code**: `status_monitor/` directory
- **Dashboard**: http://localhost:5001 (when running)

## Quick Start

```bash
cd status_monitor
python3 app.py
```

Then open your browser to: **http://localhost:5001**

## What It Shows

### Service Status
- SSH Connection status
- Python installation
- Virtual environment status
- PostgreSQL service
- FastAPI service
- Code deployment status

### System Information
- Server uptime
- Disk usage
- Memory usage
- CPU load

### Server Logs
- Real-time logs from APP-SERVER
- Auto-refreshes every 5 seconds

## Current APP-SERVER Status (from check-setup.sh)

✅ **SSH Connection** - Connected
✅ **Python 3.12.3** - Installed
✅ **pip 24.0** - Installed
✅ **Virtual Environment** - Created with 27 packages
✅ **PostgreSQL 18.1** - Running
✅ **Code Deployment** - 12 Python files deployed
✅ **Configuration** - .env file exists
⚠️ **FastAPI Service** - Not configured (expected, skipping IB Gateway for now)

## Features

- Real-time monitoring
- Auto-refresh every 5 seconds
- Color-coded status indicators
- Live log streaming
- System resource monitoring

## API Endpoints

- `GET /` - Main dashboard
- `GET /api/status` - JSON status data
- `GET /api/logs` - Server logs
- `GET /api/system-info` - System information
- `GET /api/install-status` - Detailed installation status

## Troubleshooting

If the status monitor doesn't start:

1. Check if Flask is installed:
   ```bash
   pip3 install Flask
   ```

2. Check if port 5000 is available:
   ```bash
   lsof -ti:5000
   ```

3. Start manually:
   ```bash
   cd status_monitor
   python3 app.py
   ```

4. Check for errors in the terminal output

## Next Steps

1. Start the status monitor: `cd status_monitor && python3 app.py`
2. Open browser to http://localhost:5001
3. Monitor APP-SERVER status in real-time
4. When ready, configure FastAPI service on APP-SERVER (after IB Gateway approval)

