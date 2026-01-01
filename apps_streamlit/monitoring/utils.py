"""Shared utility functions for Streamlit monitoring app."""
import subprocess
from datetime import datetime

# Configuration
APP_SERVER = "app-server"  # SSH hostname from config
APP_SERVER_PATH = "~/bifrost-trader"


def run_ssh_command(command):
    """Execute SSH command on APP-SERVER."""
    try:
        ssh_cmd = [
            "ssh",
            "-o", "ConnectTimeout=5",
            "-o", "StrictHostKeyChecking=no",
            "-o", "BatchMode=yes",
            APP_SERVER,
            command
        ]
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=15,
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timeout", "stdout": "", "stderr": "SSH command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e), "stdout": "", "stderr": str(e)}


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


def get_fastapi_logs_streaming(lines=100):
    """Get FastAPI logs with better formatting for streaming."""
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

    # If no logs found, try to diagnose
    check_file = run_ssh_command(
        "test -f /tmp/fastapi.log && echo 'exists' || echo 'not_found'"
    )
    if check_file["success"] and "exists" in check_file["stdout"]:
        check_size = run_ssh_command("wc -l /tmp/fastapi.log 2>&1 | awk '{print $1}'")
        if check_size["success"]:
            line_count = check_size["stdout"].strip()
            if line_count.isdigit():
                if int(line_count) == 0:
                    return f"Log file exists but is empty (0 lines).\n\nFastAPI may have just started or logging hasn't begun yet.\n\nCheck: ssh {APP_SERVER} 'tail -f /tmp/fastapi.log'"
                else:
                    final_try = run_ssh_command(
                        f"tail -n {min(lines, 50)} /tmp/fastapi.log"
                    )
                    if (
                        final_try["success"]
                        and final_try["stdout"].strip()
                        and len(final_try["stdout"].strip()) > 10
                    ):
                        return final_try["stdout"].strip()
                    return f"Log file exists with {line_count} lines but couldn't read content.\n\nTry manually: ssh {APP_SERVER} 'tail -n {lines} /tmp/fastapi.log'\n\nDebug: Last command returncode={check_size.get('returncode', 'N/A')}"

    test_ssh = run_ssh_command("echo 'SSH_TEST'")
    debug_info = ""
    if not test_ssh["success"]:
        debug_info = f"\n\n⚠️ SSH connection test failed: {test_ssh.get('error', 'Unknown error')}"
        if test_ssh.get("stderr"):
            debug_info += f"\nStderr: {test_ssh['stderr']}"

    return f"No logs available. FastAPI may not be running or logging is not configured.{debug_info}\n\nTo check:\n1. Verify FastAPI is running: ssh {APP_SERVER} 'ps aux | grep src.main'\n2. Check log file: ssh {APP_SERVER} 'ls -la /tmp/fastapi.log'\n3. View logs directly: ssh {APP_SERVER} 'tail -f /tmp/fastapi.log'"


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


def get_logs():
    """Get recent logs from APP-SERVER."""
    log_check = run_ssh_command(
        "tail -50 /tmp/fastapi.log 2>/dev/null || echo 'no_fastapi_log'"
    )

    if (
        "no_fastapi_log" in log_check.get("stdout", "")
        or not log_check.get("stdout", "").strip()
    ):
        log_check = run_ssh_command(
            "journalctl -u bifrost-api -n 50 --no-pager 2>/dev/null || echo 'no_systemd_logs'"
        )

    if (
        "no_systemd_logs" in log_check.get("stdout", "")
        or not log_check.get("stdout", "").strip()
    ):
        log_check = run_ssh_command(
            f"cd {APP_SERVER_PATH} && tail -50 app.log 2>/dev/null || echo 'no_app_log'"
        )

    if (
        "no_app_log" in log_check.get("stdout", "")
        or not log_check.get("stdout", "").strip()
    ):
        log_check = run_ssh_command("uptime && echo '---' && df -h | head -5")

    return log_check["stdout"] if log_check["success"] else "No logs available"

