# Streamlit Cleanup Guide

## Quick Commands

### Kill All Streamlit Processes

```bash
# Method 1: Use the script
./streamlit_apps/kill-all-streamlit.sh

# Method 2: Manual command
pkill -f streamlit

# Method 3: Kill by ports
for port in 8501 8502 8503 8504 8505; do
    lsof -ti:$port | xargs kill -9 2>/dev/null
done
```

### Start Single Instance

```bash
# Method 1: Use the restart script (kills all, then starts one)
cd streamlit_apps/monitoring
./restart-single.sh

# Method 2: Manual start
cd streamlit_apps/monitoring
streamlit run app.py
```

## Check Running Streamlit Processes

```bash
# List all Streamlit processes
ps aux | grep streamlit | grep -v grep

# Check ports in use
lsof -ti:8501,8502,8503,8504,8505
```

## Complete Cleanup and Restart

```bash
# 1. Kill all Streamlit
pkill -f streamlit

# 2. Free up ports
for port in 8501 8502 8503 8504 8505; do
    lsof -ti:$port | xargs kill -9 2>/dev/null
done

# 3. Wait a moment
sleep 2

# 4. Start single instance
cd streamlit_apps/monitoring
streamlit run app.py
```

## One-Liner

```bash
pkill -f streamlit && sleep 2 && cd streamlit_apps/monitoring && streamlit run app.py
```

