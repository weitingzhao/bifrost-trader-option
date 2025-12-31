"""Streamlit Status Monitor for APP-SERVER (10.0.0.80)."""

import streamlit as st
from datetime import datetime
import time
from utils import (
    get_status,
    get_system_info,
    get_fastapi_logs_streaming,
    get_status_icon,
    get_logs,
    run_ssh_command,
    APP_SERVER,
)

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
    
    /* Links */
    a {
        color: #60a5fa !important;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
        color: #93c5fd !important;
    }
    
    /* Status items with links */
    .status-item a {
        font-size: 12px;
        margin-right: 8px;
    }
    
    /* Smooth transitions */
    .status-item, .metric-card {
        transition: background-color 0.3s ease;
    }
    
    /* Loading indicator */
    .refresh-indicator {
        color: #60a5fa;
        font-size: 12px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    </style>
""",
    unsafe_allow_html=True,
)


# Main App
def main():
    # Initialize session state
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    if "refresh_count" not in st.session_state:
        st.session_state.refresh_count = 0

    st.title("📊 Bifrost APP-SERVER Status Monitor")

    # Sidebar - Static, doesn't refresh
    with st.sidebar:
        st.header("⚙️ Controls")
        auto_refresh = st.checkbox("Auto-refresh", value=True, key="auto_refresh")
        refresh_interval = st.slider(
            "Refresh interval (seconds)", 5, 60, 10, key="refresh_interval"
        )

        if st.button("🔄 Refresh Now", key="manual_refresh"):
            st.session_state.last_refresh = datetime.now()
            st.session_state.refresh_count += 1
            st.rerun()

        st.divider()

        # Quick Navigation
        st.header("🚀 Quick Access")
        # APP-Server Status button (parent)
        try:
            st.page_link(
                "pages/1_APP_Server_status.py",
                label="📊 APP-Server Status",
                icon="📊",
                use_container_width=True,
            )
        except:
            st.markdown(
                '[<button style="background-color: #1f77b4; color: white; border: none; '
                "padding: 10px 20px; border-radius: 5px; cursor: pointer; width: 100%; "
                'font-size: 16px; font-weight: bold;">📊 APP-Server Status</button>](/APP_Server_status)',
                unsafe_allow_html=True,
            )

        # API Logs button (child of APP-Server Status, indented)
        st.markdown('<div style="margin-left: 20px;">', unsafe_allow_html=True)
        try:
            st.page_link(
                "pages/1_API_live_logs.py",
                label="📝 API Logs",
                icon="📝",
                use_container_width=True,
            )
        except:
            st.markdown(
                '[<button style="background-color: #1f77b4; color: white; border: none; '
                "padding: 8px 16px; border-radius: 5px; cursor: pointer; width: calc(100% - 20px); "
                'font-size: 14px; font-weight: bold; margin-left: 20px;">📝 API Logs</button>](/API_live_logs)',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        st.header("📋 Quick Info")
        st.info(
            """
        This dashboard monitors the APP-SERVER (10.0.0.80) 
        deployment status and system health.
        """
        )

        # Status indicator
        st.divider()
        st.markdown(
            f"**Last Update:** {st.session_state.last_refresh.strftime('%H:%M:%S')}"
        )
        st.markdown(f"**Updates:** {st.session_state.refresh_count}")

    # Create containers for dynamic content (these will update without full page refresh)
    status_container = st.container()

    # Get status data (with caching to reduce unnecessary calls)
    with status_container:
        with st.spinner("Fetching status..."):
            status = get_status()
            system_info = get_system_info()

    # Overall Status Banner - Update timestamp
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

    # Update caption with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"Monitoring 10.0.0.80 (APP-SERVER) • Last updated: {timestamp}")

    st.markdown(
        f"""
    <div class="metric-card" style="background: {status_bg_color.get(overall_status, '#374151')}; border-left: 4px solid {'#10b981' if overall_status == 'healthy' else '#f59e0b' if overall_status == 'degraded' else '#6b7280'};">
        <h2 style="color: #ffffff; margin: 0;">{status_color.get(overall_status, '❓')} Overall Status: {overall_status.upper()}</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Service Status Columns - Use empty containers for updates
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
                <span class="{status_class}" style="font-size: 14px;">{check_status.replace('_', ' ').upper()}</span><br>
                <small style="color: #b0b0b0;">{check_data.get('message', check_data.get('version', ''))}</small>
                {service_link}
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

    # Link to dedicated FastAPI logs page
    st.info(
        "💡 **Tip:** For dedicated FastAPI live logs with independent refresh, use the [📝 FastAPI Live Logs](/FastAPI_Live_Logs) page in the sidebar menu."
    )

    log_tab1, log_tab2, log_tab3 = st.tabs(
        ["FastAPI Live Logs", "All Logs", "System Info"]
    )

    with log_tab1:
        st.markdown("**Real-time FastAPI Console Output**")

        # Get log lines setting (persistent in session state)
        if "log_lines" not in st.session_state:
            st.session_state.log_lines = 100
        log_lines = st.slider(
            "Number of log lines",
            20,
            200,
            st.session_state.log_lines,
            key="log_lines_slider",
        )
        st.session_state.log_lines = log_lines

        # Auto-refresh toggle for logs (persistent)
        if "auto_refresh_logs" not in st.session_state:
            st.session_state.auto_refresh_logs = True
        auto_refresh_logs = st.checkbox(
            "Auto-refresh logs",
            value=st.session_state.auto_refresh_logs,
            key="auto_logs_checkbox",
        )
        st.session_state.auto_refresh_logs = auto_refresh_logs

        # Use empty container for log updates
        log_display = st.empty()

        with log_display.container():
            # Get FastAPI logs
            fastapi_logs = get_fastapi_logs_streaming(lines=log_lines)

            # Format logs with better styling
            st.markdown(
                """
                <style>
                .stCodeBlock {
                    background-color: #1a1a1a !important;
                    border: 1px solid #404040;
                    border-radius: 4px;
                }
                .stCodeBlock code {
                    color: #d4d4d4 !important;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                    font-size: 12px;
                    line-height: 1.5;
                }
                .log-timestamp {
                    color: #60a5fa;
                }
                .log-error {
                    color: #ef4444;
                }
                .log-warning {
                    color: #f59e0b;
                }
                .log-info {
                    color: #10b981;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            # Display logs with syntax highlighting
            # Check if we have actual log content (not error messages)
            has_logs = (
                fastapi_logs
                and fastapi_logs.strip()
                and "No logs available" not in fastapi_logs
                and "Log file exists but is empty" not in fastapi_logs
                and len(fastapi_logs.strip()) > 20
            )  # Ensure we have substantial content

            if has_logs:
                # Split logs into lines for better display
                log_lines_list = [
                    line for line in fastapi_logs.split("\n") if line.strip()
                ]

                # Show log source info
                st.caption(
                    f"📄 Source: /tmp/fastapi.log on {APP_SERVER} | Lines: {len(log_lines_list)}"
                )

                # Create a scrollable code block
                st.code(fastapi_logs, language="text")

                # Show log stats
                error_count = sum(
                    1
                    for line in log_lines_list
                    if "ERROR" in line.upper() or "error" in line.lower()
                )
                warning_count = sum(
                    1
                    for line in log_lines_list
                    if "WARNING" in line.upper() or "warning" in line.lower()
                )
                info_count = sum(
                    1
                    for line in log_lines_list
                    if "INFO" in line.upper()
                    and "ERROR" not in line.upper()
                    and "WARNING" not in line.upper()
                )

                # Display stats
                if error_count > 0 or warning_count > 0 or info_count > 0:
                    col_err, col_warn, col_info = st.columns(3)
                    with col_err:
                        if error_count > 0:
                            st.error(f"❌ Errors: {error_count}")
                        else:
                            st.success("✅ No errors")
                    with col_warn:
                        if warning_count > 0:
                            st.warning(f"⚠️ Warnings: {warning_count}")
                        else:
                            st.success("✅ No warnings")
                    with col_info:
                        st.info(f"ℹ️ Info: {info_count}")
            else:
                # Show diagnostic information
                st.warning("⚠️ No FastAPI logs found in /tmp/fastapi.log on APP-SERVER")

                # Show what we tried
                st.info(
                    f"Attempted to retrieve logs from: `ssh {APP_SERVER} 'tail -n {log_lines} /tmp/fastapi.log'`"
                )

                # Diagnostic section
                with st.expander("🔍 Diagnostic Information"):
                    st.markdown("**Test SSH connection:**")
                    st.code(f"ssh {APP_SERVER} 'echo connected'", language="bash")

                    st.markdown("**Check FastAPI status:**")
                    st.code(
                        f"ssh {APP_SERVER} 'ps aux | grep src.main | grep -v grep'",
                        language="bash",
                    )

                    st.markdown("**Check log file:**")
                    st.code(
                        f"ssh {APP_SERVER} 'ls -la /tmp/fastapi.log'", language="bash"
                    )

                    st.markdown("**View logs directly (this should work):**")
                    st.code(
                        f"ssh {APP_SERVER} 'tail -50 /tmp/fastapi.log'", language="bash"
                    )

                    st.markdown("**Restart FastAPI with logging:**")
                    st.code(
                        f"ssh {APP_SERVER} 'pkill -f src.main && cd ~/bifrost-trader && source venv/bin/activate && nohup python -m src.main > /tmp/fastapi.log 2>&1 &'",
                        language="bash",
                    )

                    # Test the actual command - use the exact command that works manually
                    st.markdown("---")
                    st.markdown("**🔬 Live Test - Execute command now:**")
                    if st.button("Test Log Retrieval", key="test_logs"):
                        with st.spinner("Testing SSH command..."):
                            # Import run_ssh_command for testing
                            from utils import run_ssh_command

                            # Test with the exact command that works manually
                            test_result = run_ssh_command(
                                f"tail -n 100 /tmp/fastapi.log 2>&1"
                            )

                            if test_result["success"]:
                                st.success("✅ SSH command executed successfully")
                                output = test_result["stdout"].strip()
                                if output:
                                    # Show first 1000 chars
                                    preview = output[:1000] + (
                                        "..." if len(output) > 1000 else ""
                                    )
                                    st.code(preview, language="text")
                                    line_count = len(output.split("\n"))
                                    st.info(
                                        f"✅ Retrieved {line_count} lines. If you see logs above, the Streamlit app should work too."
                                    )
                                else:
                                    st.warning(
                                        "Command succeeded but returned no output. Log file might be empty."
                                    )
                                    # Show stderr if available
                                    if test_result.get("stderr"):
                                        st.code(
                                            f"Stderr: {test_result['stderr']}",
                                            language="text",
                                        )
                            else:
                                st.error(
                                    f"❌ SSH command failed (returncode: {test_result.get('returncode', 'N/A')})"
                                )
                                if test_result.get("stderr"):
                                    st.code(
                                        f"Stderr: {test_result['stderr']}",
                                        language="text",
                                    )
                                if test_result.get("error"):
                                    st.code(
                                        f"Error: {test_result['error']}",
                                        language="text",
                                    )
                                if test_result.get("stdout"):
                                    st.code(
                                        f"Stdout: {test_result['stdout']}",
                                        language="text",
                                    )

                                # Additional debug info
                                st.markdown("**Debug Information:**")
                                st.json(
                                    {
                                        "command": f"tail -n 100 /tmp/fastapi.log",
                                        "success": test_result.get("success", False),
                                        "returncode": test_result.get(
                                            "returncode", "N/A"
                                        ),
                                        "stdout_length": len(
                                            test_result.get("stdout", "")
                                        ),
                                        "stderr_length": len(
                                            test_result.get("stderr", "")
                                        ),
                                    }
                                )

        # Auto-refresh logs if enabled (separate from main refresh)
        if auto_refresh_logs and auto_refresh:
            # Only refresh logs tab, not entire page
            time.sleep(1)  # Shorter interval for logs
            # Update just the log display
            if (
                datetime.now()
                - st.session_state.get("last_log_refresh", datetime.now())
            ).total_seconds() >= 2:
                st.session_state.last_log_refresh = datetime.now()
                st.rerun()

    with log_tab2:
        st.markdown("**All Server Logs**")
        logs = get_logs()
        st.markdown(
            """
            <style>
            .stCodeBlock {
                background-color: #1a1a1a !important;
                border: 1px solid #404040;
            }
            .stCodeBlock code {
                color: #d4d4d4 !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.code(logs, language="bash")

        # Quick actions
        st.markdown("**Quick Actions:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📋 Copy Logs"):
                st.code(logs, language="bash")
        with col2:
            if st.button("🔄 Refresh Logs"):
                st.rerun()
        with col3:
            st.markdown(f"[🔗 SSH to Server](ssh://app-server)")

    with log_tab3:
        st.json(
            {
                "server": status["server"],
                "timestamp": status["timestamp"],
                "checks": status["checks"],
                "system_info": system_info,
            }
        )

    # Smart auto-refresh - only refresh data, not entire page
    if auto_refresh:
        # Use time-based refresh instead of immediate rerun
        elapsed = (datetime.now() - st.session_state.last_refresh).total_seconds()
        if elapsed >= refresh_interval:
            st.session_state.last_refresh = datetime.now()
            st.session_state.refresh_count += 1
            # Use st.rerun() but with minimal disruption
            time.sleep(0.1)  # Small delay to allow UI to update
            st.rerun()
        else:
            # Show countdown
            remaining = refresh_interval - elapsed
            st.sidebar.caption(f"⏱️ Next refresh in {int(remaining)}s")


if __name__ == "__main__":
    main()
