"""Streamlit Status Monitor for APP-SERVER (10.0.0.80)."""

import streamlit as st
import subprocess
import json
from datetime import datetime
import time

# Configuration
APP_SERVER = "app-server"  # SSH hostname from config
APP_SERVER_PATH = "~/bifrost-trader"

# Page config with dark theme
st.set_page_config(
    page_title="Bifrost APP-SERVER Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS with dark theme
st.markdown(
    """
    <style>
    /* Main background */
    .main .block-container {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    /* Status colors */
    .status-healthy { 
        color: #10b981; 
        font-weight: bold; 
    }
    .status-degraded { 
        color: #f59e0b; 
        font-weight: bold; 
    }
    .status-offline { 
        color: #ef4444; 
        font-weight: bold; 
    }
    
    /* Metric cards */
    .metric-card { 
        background: #2d2d2d; 
        padding: 15px; 
        border-radius: 8px; 
        border-left: 4px solid #667eea;
        color: #e0e0e0;
    }
    
    /* Status items */
    .status-item {
        background: #2d2d2d;
        padding: 12px;
        margin: 8px 0;
        border-radius: 6px;
        border: 1px solid #404040;
        color: #e0e0e0;
    }
    
    /* Text colors */
    p, div, span {
        color: #e0e0e0 !important;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background-color: #1a1a1a !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #b0b0b0 !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #252525;
    }
    
    /* Caption */
    .stCaption {
        color: #b0b0b0 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def run_ssh_command(command):
    """Execute SSH command on APP-SERVER."""
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=5", APP_SERVER, command],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_status():
    """Get overall status of APP-SERVER."""
    status = {
        "timestamp": datetime.now().isoformat(),
        "server": "10.0.0.80 (APP-SERVER)",
        "checks": {},
    }

    # Check SSH connection
    ssh_check = run_ssh_command("echo 'connected'")
    status["checks"]["ssh"] = {
        "status": "online" if ssh_check["success"] else "offline",
        "message": "Connected" if ssh_check["success"] else "Cannot connect",
    }

    # Check Python
    python_check = run_ssh_command("python3 --version")
    status["checks"]["python"] = {
        "status": "installed" if python_check["success"] else "not_installed",
        "version": python_check["stdout"].strip() if python_check["success"] else "N/A",
    }

    # Check venv
    venv_check = run_ssh_command(
        f"cd {APP_SERVER_PATH} && test -d venv && echo 'exists' || echo 'not_found'"
    )
    status["checks"]["venv"] = {
        "status": "created" if "exists" in venv_check["stdout"] else "not_created",
        "message": (
            "Virtual environment exists"
            if "exists" in venv_check["stdout"]
            else "Virtual environment not created"
        ),
    }

    # Check PostgreSQL
    pg_check = run_ssh_command(
        "systemctl is-active postgresql 2>/dev/null || service postgresql status 2>/dev/null | grep -q running && echo 'running' || echo 'not_running'"
    )
    status["checks"]["postgresql"] = {
        "status": "running" if "running" in pg_check["stdout"] else "not_running",
        "message": (
            "PostgreSQL is running"
            if "running" in pg_check["stdout"]
            else "PostgreSQL not running or not installed"
        ),
    }

    # Check FastAPI service (systemd or process)
    fastapi_systemd = run_ssh_command(
        "systemctl is-active bifrost-api 2>/dev/null || echo 'not_active'"
    )
    fastapi_process = run_ssh_command("ps aux | grep 'src.main' | grep -v grep | wc -l")
    fastapi_port = run_ssh_command(
        "curl -s http://localhost:8000/api/health >/dev/null 2>&1 && echo 'responding' || echo 'not_responding'"
    )

    # Determine status
    is_running = (
        fastapi_systemd["stdout"].strip() == "active"
        or (fastapi_process["success"] and int(fastapi_process["stdout"].strip()) > 0)
        or fastapi_port["stdout"].strip() == "responding"
    )

    if is_running:
        status["checks"]["fastapi"] = {
            "status": "running",
            "message": "FastAPI is running (systemd service or manual process)",
        }
    else:
        status["checks"]["fastapi"] = {
            "status": "not_running",
            "message": "FastAPI service not running",
        }

    # Check if code is deployed
    code_check = run_ssh_command(
        f"cd {APP_SERVER_PATH} && test -f src/main.py && echo 'deployed' || echo 'not_deployed'"
    )
    status["checks"]["code"] = {
        "status": "deployed" if "deployed" in code_check["stdout"] else "not_deployed",
        "message": (
            "Code is deployed"
            if "deployed" in code_check["stdout"]
            else "Code not found"
        ),
    }

    # Overall status
    all_checks = [v["status"] for v in status["checks"].values()]
    if all(
        c in ["online", "installed", "created", "running", "deployed"]
        for c in all_checks
    ):
        status["overall"] = "healthy"
    elif any(
        c in ["offline", "not_installed", "not_created", "not_running", "not_deployed"]
        for c in all_checks
    ):
        status["overall"] = "degraded"
    else:
        status["overall"] = "unknown"

    return status


def get_system_info():
    """Get system information from APP-SERVER."""
    info = {}

    # Uptime
    uptime = run_ssh_command("uptime")
    info["uptime"] = uptime["stdout"].strip() if uptime["success"] else "N/A"

    # Disk usage
    disk = run_ssh_command("df -h / | tail -1")
    info["disk"] = disk["stdout"].strip() if disk["success"] else "N/A"

    # Memory
    memory = run_ssh_command("free -h | grep Mem")
    info["memory"] = memory["stdout"].strip() if memory["success"] else "N/A"

    # CPU load
    load = run_ssh_command("cat /proc/loadavg")
    info["load"] = load["stdout"].strip() if load["success"] else "N/A"

    return info


def get_logs():
    """Get recent logs from APP-SERVER."""
    # Try to get systemd logs
    log_check = run_ssh_command(
        "journalctl -u bifrost-api -n 50 --no-pager 2>/dev/null || echo 'no_logs'"
    )

    if "no_logs" in log_check["stdout"]:
        # Try to get logs from file
        log_check = run_ssh_command(
            f"cd {APP_SERVER_PATH} && tail -50 app.log 2>/dev/null || echo 'no_log_file'"
        )

    if "no_log_file" in log_check["stdout"]:
        # Get general system info
        log_check = run_ssh_command("uptime && echo '---' && df -h | head -5")

    return log_check["stdout"] if log_check["success"] else "No logs available"


def get_status_icon(status):
    """Get emoji icon for status."""
    icons = {
        "online": "🟢",
        "offline": "🔴",
        "installed": "✅",
        "not_installed": "❌",
        "created": "✅",
        "not_created": "❌",
        "running": "🟢",
        "not_running": "🟡",
        "deployed": "✅",
        "not_deployed": "❌",
        "healthy": "🟢",
        "degraded": "🟡",
        "unknown": "⚪",
    }
    return icons.get(status, "❓")


# Main App
def main():
    st.title("📊 Bifrost APP-SERVER Status Monitor")
    st.caption(
        f"Monitoring 10.0.0.80 (APP-SERVER) • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Controls")
        auto_refresh = st.checkbox("Auto-refresh", value=True)
        refresh_interval = st.slider("Refresh interval (seconds)", 5, 60, 10)

        if st.button("🔄 Refresh Now"):
            st.rerun()

        st.divider()
        st.header("📋 Quick Info")
        st.info(
            """
        This dashboard monitors the APP-SERVER (10.0.0.80) 
        deployment status and system health.
        """
        )

    # Get status data
    with st.spinner("Fetching status..."):
        status = get_status()
        system_info = get_system_info()

    # Overall Status Banner
    overall_status = status["overall"]
    status_color = {
        "healthy": "🟢",
        "degraded": "🟡",
        "unknown": "⚪",
    }

    status_bg_color = {
        "healthy": "#064e3b",
        "degraded": "#78350f",
        "unknown": "#374151",
    }

    st.markdown(
        f"""
    <div class="metric-card" style="background: {status_bg_color.get(overall_status, '#374151')}; border-left: 4px solid {'#10b981' if overall_status == 'healthy' else '#f59e0b' if overall_status == 'degraded' else '#6b7280'};">
        <h2 style="color: #ffffff; margin: 0;">{status_color.get(overall_status, '❓')} Overall Status: {overall_status.upper()}</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Service Status Columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔌 Service Status")
        for check_name, check_data in status["checks"].items():
            check_status = check_data["status"]
            icon = get_status_icon(check_status)

            status_class = (
                "status-healthy"
                if check_status
                in ["online", "installed", "created", "running", "deployed"]
                else "status-degraded"
            )

            st.markdown(
                f"""
            <div class="status-item">
                <strong style="color: #ffffff; font-size: 16px;">{icon} {check_name.replace('_', ' ').title()}</strong><br>
                <span class="{status_class}" style="font-size: 14px;">{check_status.replace('_', ' ').upper()}</span><br>
                <small style="color: #b0b0b0;">{check_data.get('message', check_data.get('version', ''))}</small>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with col2:
        st.subheader("💻 System Information")

        # Uptime
        if "uptime" in system_info:
            st.metric(
                "Uptime",
                (
                    system_info["uptime"].split(",")[0]
                    if system_info["uptime"] != "N/A"
                    else "N/A"
                ),
            )

        # Memory
        if "memory" in system_info and system_info["memory"] != "N/A":
            mem_parts = system_info["memory"].split()
            if len(mem_parts) >= 2:
                st.metric(
                    "Memory",
                    (
                        mem_parts[1] + " / " + mem_parts[2]
                        if len(mem_parts) >= 3
                        else mem_parts[1]
                    ),
                )

        # Disk
        if "disk" in system_info and system_info["disk"] != "N/A":
            disk_parts = system_info["disk"].split()
            if len(disk_parts) >= 4:
                st.metric(
                    "Disk Usage", f"{disk_parts[2]} / {disk_parts[1]} ({disk_parts[4]})"
                )

        # CPU Load
        if "load" in system_info and system_info["load"] != "N/A":
            load_parts = system_info["load"].split()
            if len(load_parts) >= 3:
                st.metric("CPU Load (1m)", load_parts[0])

    st.divider()

    # Logs Section
    st.subheader("📝 Server Logs")

    log_tab1, log_tab2 = st.tabs(["Live Logs", "System Info"])

    with log_tab1:
        logs = get_logs()
        st.markdown(
            """
        <style>
        .stCodeBlock {
            background-color: #1a1a1a !important;
        }
        .stCodeBlock code {
            color: #d4d4d4 !important;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )
        st.code(logs, language="bash")

    with log_tab2:
        st.json(
            {
                "server": status["server"],
                "timestamp": status["timestamp"],
                "checks": status["checks"],
                "system_info": system_info,
            }
        )

    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
