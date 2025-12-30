# Streamlit Status Monitor Guide

## Overview

A modern, interactive Streamlit-based status monitoring dashboard for APP-SERVER (10.0.0.80).

## Location

- **Code**: `streamlit_apps/monitoring/` directory
- **Dashboard**: http://localhost:8501 (when running)

## Quick Start

### Option 1: Using the startup script

```bash
cd streamlit_apps/monitoring
./start.sh
```

### Option 2: Direct Streamlit command

```bash
cd streamlit_apps/monitoring
streamlit run app.py
```

The dashboard will automatically open in your browser!

## Features

### 📊 Real-time Monitoring
- Auto-refresh capability (configurable interval)
- Live status updates
- System resource monitoring

### 🔌 Service Status Checks
- SSH Connection status
- Python installation
- Virtual environment status
- PostgreSQL service
- FastAPI service
- Code deployment status

### 💻 System Information
- Server uptime
- Memory usage
- Disk usage
- CPU load average

### 📝 Live Logs
- Real-time server logs
- Systemd journal logs
- System information

## Dashboard Layout

1. **Header**: Overall status banner with color-coded indicators
2. **Service Status Panel**: All service checks with status icons
3. **System Info Panel**: Real-time system metrics
4. **Logs Section**: Live logs with tabs for different views
5. **Sidebar**: Controls for auto-refresh and manual refresh

## Status Indicators

- 🟢 **Green** - Healthy/Online/Running
- 🟡 **Yellow** - Degraded/Warning/Not Running
- 🔴 **Red** - Offline/Error
- ⚪ **White** - Unknown status

## Configuration

Edit `app.py` to change:

```python
APP_SERVER = "app-server"  # SSH hostname
APP_SERVER_PATH = "~/bifrost-trader"  # Remote path
```

## Controls

### Sidebar Options

- **Auto-refresh**: Toggle automatic updates
- **Refresh Interval**: Set update frequency (5-60 seconds)
- **Refresh Now**: Manual refresh button

### Tabs

- **Live Logs**: Real-time server logs
- **System Info**: Detailed JSON status

## Current APP-SERVER Status

Based on the setup check:

✅ **SSH Connection** - Connected  
✅ **Python 3.12.3** - Installed  
✅ **Virtual Environment** - Created (27 packages)  
✅ **PostgreSQL 18.1** - Running  
✅ **Code Deployment** - 12 Python files deployed  
⚠️ **FastAPI Service** - Not configured (expected, IB Gateway pending)

## Troubleshooting

### Streamlit Not Found

```bash
pip install streamlit
```

### Cannot Connect to APP-SERVER

1. Test SSH connection:
   ```bash
   ssh app-server
   ```

2. Check SSH config:
   ```bash
   cat ~/.ssh/config | grep app-server
   ```

### Port Already in Use

Streamlit will automatically use the next available port if 8501 is busy.

### App Not Updating

- Check auto-refresh is enabled in sidebar
- Click "Refresh Now" for manual update
- Check terminal for errors

## Stopping the App

Press `Ctrl+C` in the terminal where Streamlit is running.

## Comparison with Flask Version

### Advantages of Streamlit

- ✅ More interactive UI
- ✅ Built-in auto-refresh
- ✅ Better data visualization
- ✅ Easier to customize
- ✅ No HTML/CSS/JavaScript needed
- ✅ Automatic browser opening

### Flask Version

- Still available in `status_monitor/` directory
- Can run on port 5001 (if needed)
- More control over HTML/CSS

## Next Steps

1. **Monitor APP-SERVER**: Use the dashboard to track status
2. **Configure Services**: When IB Gateway is approved, set up FastAPI service
3. **Add More Apps**: Create additional Streamlit apps in `streamlit_apps/` directory

## Future Enhancements

- Strategy analysis dashboard
- Options chain visualizer
- Historical data charts
- ML model monitoring
- Alert notifications

