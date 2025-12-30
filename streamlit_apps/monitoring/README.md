# APP-SERVER Status Monitor (Streamlit)

Real-time status monitoring dashboard for APP-SERVER (10.0.0.80) built with Streamlit.

## Features

- 📊 Real-time status monitoring
- 🔌 Service health checks
- 💻 System information (CPU, memory, disk)
- 📝 Live server logs
- 🔄 Auto-refresh capability
- 🎨 Modern, interactive UI

## Quick Start

### Install Dependencies

```bash
pip install streamlit
```

Or:

```bash
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## What It Monitors

1. **SSH Connection** - Connectivity to APP-SERVER
2. **Python** - Python installation and version
3. **Virtual Environment** - venv status and packages
4. **PostgreSQL** - Database service status
5. **FastAPI Service** - Application service status
6. **Code Deployment** - Project files verification
7. **System Resources** - CPU, memory, disk usage

## Configuration

Edit the configuration at the top of `app.py`:

```python
APP_SERVER = "app-server"  # SSH hostname
APP_SERVER_PATH = "~/bifrost-trader"  # Path on remote server
```

## Usage

1. **Auto-refresh**: Enable in sidebar to automatically update status
2. **Refresh Interval**: Adjust how often the dashboard updates (5-60 seconds)
3. **Manual Refresh**: Click "Refresh Now" button in sidebar
4. **Logs**: View live logs in the "Live Logs" tab
5. **System Info**: View detailed JSON in "System Info" tab

## Status Indicators

- 🟢 **Green** - Healthy/Online/Running
- 🟡 **Yellow** - Degraded/Warning
- 🔴 **Red** - Offline/Not Running/Error
- ⚪ **White** - Unknown status

## Troubleshooting

### Cannot Connect to APP-SERVER

1. Verify SSH connection:
   ```bash
   ssh app-server
   ```

2. Check SSH config:
   ```bash
   cat ~/.ssh/config | grep app-server
   ```

### Streamlit Not Found

```bash
pip install streamlit
```

### Port Already in Use

Streamlit uses port 8501 by default. If it's in use, Streamlit will automatically use the next available port.

