"""APP-Server Status Page - Service Status, System Information, and Overall Status only."""

import streamlit as st
from datetime import datetime
import sys
import os

# Add parent directory to path to import utils
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from utils import get_status, get_system_info, get_status_icon, run_ssh_command

# Page config
st.set_page_config(
    page_title="APP-Server Status",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for dark theme
st.markdown(
    """
    <style>
    .main .block-container {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    h1, h2, h3 {
        color: #ffffff !important;
    }
    .status-item {
        background-color: #2a2a2a;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #404040;
    }
    .metric-card {
        background: #2d2d2d;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        color: #e0e0e0;
    }
    .status-healthy {
        color: #10b981;
        font-weight: bold;
    }
    .status-degraded {
        color: #f59e0b;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Initialize session state
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# Main Page
st.title("📊 APP-Server Status Monitor")
st.caption(
    f"Service status for APP-SERVER (10.0.0.80) • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Controls")

    if st.button("🔄 Refresh Now", key="manual_refresh"):
        st.session_state.last_refresh = datetime.now()
        st.rerun()

    st.divider()

    # Status info
    st.markdown(
        f"**Last Update:** {st.session_state.last_refresh.strftime('%H:%M:%S')}"
    )

    st.divider()
    st.header("📋 Quick Actions")

    # Quick navigation - back to dashboard
    try:
        st.page_link("app.py", label="📊 Main Dashboard", icon="📊")
    except:
        if st.button(
            "📊 Main Dashboard", key="goto_dashboard", use_container_width=True
        ):
            st.switch_page("/")

    # Link to API Logs (child page)
    try:
        st.page_link("pages/1_API_live_logs.py", label="📝 API Logs", icon="📝")
    except:
        if st.button("📝 API Logs", key="goto_logs", use_container_width=True):
            st.switch_page("API_live_logs")

    st.divider()

    # External links
    st.markdown("**External Links:**")
    st.markdown(f"[🔗 FastAPI API Docs](http://10.0.0.80:8000/docs)")
    st.markdown(f"[🔗 Health Check](http://10.0.0.80:8000/api/health)")

# Get status data
with st.spinner("Fetching status..."):
    status = get_status()
    system_info = get_system_info()

# Overall Status Banner
if status and "overall" in status:
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
        <div class="metric-card" style="background: {status_bg_color.get(overall_status, '#374151')}; border-left: 4px solid {'#10b981' if overall_status == 'healthy' else '#f59e0b' if overall_status == 'degraded' else '#6b7280'}; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <h2 style="color: #ffffff; margin: 0;">{status_color.get(overall_status, '❓')} Overall Status: {overall_status.upper()}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

# Service Status and System Information in columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔌 Service Status")

    if status and "checks" in status:
        # Display all service checks
        for check_name, check_data in status["checks"].items():
            check_status = check_data["status"]
            icon = get_status_icon(check_status)

            status_class = (
                "status-healthy"
                if check_status
                in ["online", "installed", "created", "running", "deployed"]
                else "status-degraded"
            )

            status_color = (
                "#10b981"
                if check_status
                in ["online", "installed", "created", "running", "deployed"]
                else "#ef4444"
            )

            # Add clickable links for PostgreSQL and FastAPI
            service_link = ""
            if check_name == "postgresql" and check_status == "running":
                service_link = '<br><a href="http://10.0.0.80:5432" target="_blank" style="color: #60a5fa; text-decoration: none;">🔗 Connect to PostgreSQL</a> | <a href="http://10.0.0.80" target="_blank" style="color: #60a5fa; text-decoration: none;">📊 pgAdmin</a>'
            elif check_name == "fastapi" and check_status == "running":
                service_link = '<br><a href="http://10.0.0.80:8000" target="_blank" style="color: #60a5fa; text-decoration: none;">🔗 API: http://10.0.0.80:8000</a> | <a href="http://10.0.0.80:8000/docs" target="_blank" style="color: #60a5fa; text-decoration: none;">📚 API Docs</a> | <a href="http://10.0.0.80:8000/api/health" target="_blank" style="color: #60a5fa; text-decoration: none;">❤️ Health Check</a>'

            st.markdown(
                f"""
                <div class="status-item">
                    <strong style="color: #ffffff; font-size: 16px;">{icon} {check_name.replace('_', ' ').title()}</strong><br>
                    <span class="{status_class}" style="font-size: 14px; color: {status_color};">{check_status.replace('_', ' ').upper()}</span><br>
                    <small style="color: #b0b0b0;">{check_data.get('message', check_data.get('version', ''))}</small>
                    {service_link}
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.warning("⚠️ Unable to retrieve service status")

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
        if len(disk_parts) >= 5:
            st.metric(
                "Disk Usage",
                disk_parts[4] + " / " + disk_parts[1],
            )

    # CPU Load
    if "load" in system_info and system_info["load"] != "N/A":
        load_parts = system_info["load"].split(",")
        if len(load_parts) >= 3:
            st.metric("CPU Load (1m)", load_parts[0])
