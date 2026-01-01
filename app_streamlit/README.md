# Streamlit Applications

This directory contains Streamlit-based web applications for the Bifrost Options Trading Strategy Analyzer project.

## Available Apps

### 📊 Monitoring Dashboard
**Location**: `monitoring/`

Real-time status monitoring dashboard for APP-SERVER (10.0.0.80).

**Run**:
```bash
cd monitoring
streamlit run app.py
```

**Features**:
- Service health checks
- System information
- Live server logs
- Auto-refresh

## Installation

Install Streamlit for all apps:

```bash
pip install streamlit
```

Or install per-app requirements:

```bash
cd monitoring
pip install -r requirements.txt
```

## Running Apps

Each app can be run independently:

```bash
streamlit run <app_directory>/app.py
```

Streamlit will automatically open the app in your browser at `http://localhost:8501`

## Future Apps

Additional Streamlit applications can be added here:
- Strategy analysis dashboard
- Options chain visualizer
- Historical data viewer
- ML model monitoring

