# Streamlit Monitoring Dashboard

Real-time status monitoring dashboard for APP-SERVER (10.0.0.80).

## Pages

### 📊 Main Dashboard (`app.py`)
- Overall server status
- Service health checks
- System information
- Quick log view

### 📝 FastAPI Live Logs (`pages/1_📝_FastAPI_Live_Logs.py`)
- Dedicated page for FastAPI console output
- Independent auto-refresh (1-10 seconds)
- Real-time log streaming
- Error/warning/info statistics
- Quick links to API docs

## Quick Start

```bash
cd streamlit_apps/monitoring
streamlit run app.py
```

Access at: **http://localhost:8501**

## Features

- **Multi-page Navigation**: Use sidebar to switch between dashboard and logs
- **Real-time Monitoring**: Auto-refresh with configurable intervals
- **Dark Theme**: Optimized for readability
- **Service Links**: Clickable links to PostgreSQL and FastAPI services
- **Log Statistics**: Error/warning counts and analysis
- **Smart Refresh**: Only updates when needed, minimal page disruption

## Navigation

- **Main Dashboard**: Overview of all services and system status
- **FastAPI Live Logs**: Dedicated page for continuous log monitoring

## Configuration

Edit `app.py` to change:
- `APP_SERVER`: SSH hostname (default: "app-server")
- `APP_SERVER_PATH`: Remote project path (default: "~/bifrost-trader")

