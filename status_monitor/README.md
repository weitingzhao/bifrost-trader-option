# Status Monitor

Web-based status monitoring dashboard for APP-SERVER (10.0.0.80).

## Features

- Real-time status monitoring of APP-SERVER
- Service health checks (SSH, Python, PostgreSQL, FastAPI, etc.)
- System information (uptime, disk, memory, CPU)
- Live server logs
- Auto-refresh every 5 seconds

## Quick Start

```bash
cd status_monitor
./start.sh
```

Or manually:

```bash
python3 app.py
```

Then open your browser to: **http://localhost:5001**

## API Endpoints

- `GET /` - Dashboard page
- `GET /api/status` - Overall status and health checks
- `GET /api/logs` - Recent server logs
- `GET /api/system-info` - System information
- `GET /api/install-status` - Detailed installation status

## What It Monitors

1. **SSH Connection** - Can connect to APP-SERVER
2. **Python** - Python version and installation
3. **Virtual Environment** - venv exists and packages installed
4. **PostgreSQL** - Database service status
5. **FastAPI Service** - Application service status
6. **Code Deployment** - Project files present
7. **System Resources** - CPU, memory, disk usage

## Status Colors

- 🟢 **Green** - Healthy/Online/Running
- 🟡 **Yellow** - Degraded/Warning
- 🔴 **Red** - Offline/Not Running/Error

## Stopping the Monitor

Press `Ctrl+C` in the terminal, or:

```bash
pkill -f "python3.*status_monitor"
```

