"""API Logs Page - Separate menu for real-time log monitoring."""

import streamlit as st
from datetime import datetime
import time
import sys
import os

# Add parent directory to path to import utils
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from utils import run_ssh_command, APP_SERVER, APP_SERVER_PATH

# Page config - This makes it appear in the sidebar menu
st.set_page_config(
    page_title="API Logs",
    page_icon="📝",
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
    </style>
    """,
    unsafe_allow_html=True,
)


def get_fastapi_logs(lines=100):
    """Get FastAPI logs from APP-SERVER."""
    log_commands = [
        f"tail -n {lines} /tmp/fastapi.log 2>&1",
        f"tail -{lines} /tmp/fastapi.log 2>&1",
        f"journalctl -u bifrost-api -n {lines} --no-pager 2>&1",
        f"cd {APP_SERVER_PATH} && tail -n {lines} app.log 2>&1",
    ]

    for cmd in log_commands:
        result = run_ssh_command(cmd)
        if result["success"]:
            output = result["stdout"].strip()
            if output and len(output) > 10:
                lower_output = output.lower()
                if (
                    "not found" not in lower_output
                    and "no such file" not in lower_output
                    and "no entries" not in lower_output
                    and "cannot access" not in lower_output
                    and "permission denied" not in lower_output
                    and "is a directory" not in lower_output
                ):
                    return output

    return None


# Initialize session state
if "log_lines" not in st.session_state:
    st.session_state.log_lines = 30  # Default to 30 rows
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True
if "refresh_interval" not in st.session_state:
    st.session_state.refresh_interval = 2
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# Main Page
st.title("📝 API Logs")
st.caption(
    f"Real-time console output from APP-SERVER (10.0.0.80) • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Log Controls")

    # Log lines - Fixed to 30 rows
    st.info("📊 Showing latest **30 rows** (newest on top)")
    log_lines = 30  # Fixed to 30 rows as requested
    st.session_state.log_lines = log_lines

    # Auto-refresh
    auto_refresh = st.checkbox(
        "Auto-refresh logs",
        value=st.session_state.auto_refresh,
        key="auto_refresh_checkbox",
    )
    st.session_state.auto_refresh = auto_refresh

    # Refresh interval
    if auto_refresh:
        refresh_interval = st.slider(
            "Refresh interval (seconds)",
            1,
            10,
            st.session_state.refresh_interval,
            key="refresh_interval_slider",
        )
        st.session_state.refresh_interval = refresh_interval

    # Manual refresh button
    if st.button("🔄 Refresh Now", key="manual_refresh"):
        st.session_state.last_refresh = datetime.now()
        st.rerun()

    st.divider()

    # Status info
    st.markdown(
        f"**Last Update:** {st.session_state.last_refresh.strftime('%H:%M:%S')}"
    )
    if auto_refresh:
        elapsed = (datetime.now() - st.session_state.last_refresh).total_seconds()
        remaining = max(0, refresh_interval - elapsed)
        st.caption(f"⏱️ Next refresh in {int(remaining)}s")

    st.divider()
    st.header("📋 Quick Actions")

    # Quick navigation - back to dashboard
    try:
        st.page_link("app.py", label="📊 Back to Dashboard", icon="📊")
    except:
        # Fallback: Navigate to main page
        if st.button(
            "📊 Back to Dashboard", key="goto_dashboard", use_container_width=True
        ):
            # Use "/" to go to main page
            st.switch_page("/")

    st.divider()

    # External links
    st.markdown("**External Links:**")
    st.markdown(f"[🔗 FastAPI API Docs](http://10.0.0.80:8000/docs)")
    st.markdown(f"[🔗 Health Check](http://10.0.0.80:8000/api/health)")

# Main Content - Server Logs Only
st.subheader("📝 Server Logs")

log_container = st.container()

with log_container:
    # Get logs
    with st.spinner("Fetching FastAPI logs..."):
        fastapi_logs = get_fastapi_logs(lines=log_lines)

    if fastapi_logs:
        # Split logs into lines
        log_lines_list = [line for line in fastapi_logs.split("\n") if line.strip()]

        # Reverse order: newest on top (last lines first)
        log_lines_list.reverse()

        # Limit to 30 rows (in case we got more)
        log_lines_list = log_lines_list[:30]

        # Join back with newlines
        reversed_logs = "\n".join(log_lines_list)

        # Show log source and stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"📄 Source: /tmp/fastapi.log on {APP_SERVER}")
        with col2:
            st.caption(f"📊 Showing: {len(log_lines_list)} rows (newest on top)")
        with col3:
            # Calculate stats
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
            st.caption(
                f"❌ Errors: {error_count} | ⚠️ Warnings: {warning_count} | ℹ️ Info: {info_count}"
            )

        st.divider()

        # Display logs (newest on top)
        st.code(reversed_logs, language="text")

        # Show stats
        if error_count > 0 or warning_count > 0:
            st.divider()
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
                st.info(f"ℹ️ Info Messages: {info_count}")
    else:
        st.warning("⚠️ No FastAPI logs found")

        # Diagnostic section
        with st.expander("🔍 Diagnostic Information"):
            st.markdown("**Test SSH connection:**")
            test_ssh = run_ssh_command("echo 'SSH_TEST'")
            if test_ssh["success"]:
                st.success("✅ SSH connection working")
            else:
                st.error(
                    f"❌ SSH connection failed: {test_ssh.get('error', 'Unknown')}"
                )

            st.markdown("**Check FastAPI status:**")
            st.code(
                f"ssh {APP_SERVER} 'ps aux | grep src.main | grep -v grep'",
                language="bash",
            )

            st.markdown("**Check log file:**")
            st.code(f"ssh {APP_SERVER} 'ls -la /tmp/fastapi.log'", language="bash")

            st.markdown("**View logs directly:**")
            st.code(f"ssh {APP_SERVER} 'tail -f /tmp/fastapi.log'", language="bash")

            # Test button
            if st.button("🔬 Test Log Retrieval", key="test_logs"):
                with st.spinner("Testing..."):
                    test_result = run_ssh_command(f"tail -n 50 /tmp/fastapi.log 2>&1")
                    if test_result["success"]:
                        if test_result["stdout"].strip():
                            st.success("✅ Log retrieval works!")
                            st.code(test_result["stdout"][:500], language="text")
                        else:
                            st.warning("Command succeeded but no output")
                    else:
                        st.error(f"❌ Failed: {test_result.get('error', 'Unknown')}")

# Auto-refresh logic
if auto_refresh:
    elapsed = (datetime.now() - st.session_state.last_refresh).total_seconds()
    if elapsed >= refresh_interval:
        st.session_state.last_refresh = datetime.now()
        time.sleep(0.1)
        st.rerun()
    else:
        # Show countdown
        remaining = refresh_interval - elapsed
        time.sleep(0.5)  # Small delay to update UI
        pass
