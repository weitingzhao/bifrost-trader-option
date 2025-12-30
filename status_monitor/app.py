"""Status monitoring web GUI for APP-SERVER."""

from flask import Flask, render_template, jsonify
import subprocess
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Configuration
APP_SERVER = "app-server"  # SSH hostname from config
APP_SERVER_PATH = "~/bifrost-trader"


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


@app.route("/")
def index():
    """Main dashboard page."""
    return render_template("dashboard.html")


@app.route("/api/status")
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

    # Check FastAPI service
    fastapi_check = run_ssh_command(
        "systemctl is-active bifrost-api 2>/dev/null || echo 'not_active'"
    )
    status["checks"]["fastapi"] = {
        "status": (
            "running" if fastapi_check["stdout"].strip() == "active" else "not_running"
        ),
        "message": (
            "FastAPI service is running"
            if fastapi_check["stdout"].strip() == "active"
            else "FastAPI service not running"
        ),
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

    return jsonify(status)


@app.route("/api/logs")
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

    return jsonify(
        {
            "timestamp": datetime.now().isoformat(),
            "logs": (
                log_check["stdout"].split("\n")
                if log_check["success"]
                else ["No logs available"]
            ),
            "source": (
                "systemd"
                if "journalctl" in str(log_check)
                else "file" if "app.log" in str(log_check) else "system"
            ),
        }
    )


@app.route("/api/system-info")
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

    return jsonify(
        {
            "timestamp": datetime.now().isoformat(),
            "server": "10.0.0.80 (APP-SERVER)",
            "info": info,
        }
    )


@app.route("/api/install-status")
def get_install_status():
    """Get detailed installation status."""
    status = {}

    # Check Python packages
    pip_check = run_ssh_command(
        f"cd {APP_SERVER_PATH} && source venv/bin/activate && pip list 2>/dev/null | head -20 || echo 'venv_not_ready'"
    )
    status["python_packages"] = (
        pip_check["stdout"] if pip_check["success"] else "Virtual environment not ready"
    )

    # Check PostgreSQL
    pg_version = run_ssh_command("psql --version 2>/dev/null || echo 'not_installed'")
    status["postgresql_version"] = (
        pg_version["stdout"].strip() if pg_version["success"] else "Not installed"
    )

    # Check database
    db_check = run_ssh_command(
        "sudo -u postgres psql -l 2>/dev/null | grep options_db || echo 'database_not_found'"
    )
    status["database"] = (
        "options_db exists"
        if "options_db" in db_check["stdout"]
        else "Database not created"
    )

    # Check project files
    files_check = run_ssh_command(
        f"cd {APP_SERVER_PATH} && ls -la src/ 2>/dev/null | head -10 || echo 'files_not_found'"
    )
    status["project_files"] = (
        files_check["stdout"] if files_check["success"] else "Files not found"
    )

    return jsonify({"timestamp": datetime.now().isoformat(), "status": status})


if __name__ == "__main__":
    print("Starting Status Monitor on http://localhost:5001")
    print(f"Monitoring APP-SERVER: {APP_SERVER} (10.0.0.80)")
    app.run(host="0.0.0.0", port=5001, debug=True)
