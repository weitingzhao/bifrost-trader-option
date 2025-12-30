#!/bin/bash
# Test SSH connections to all servers

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/servers.conf"

server_names=("app-server" "web-server" "gpu-server")

echo "Testing SSH connections..."
echo "=========================="

for server in "${server_names[@]}"; do
    echo -n "Testing $server... "
    if ssh -o ConnectTimeout=5 -o BatchMode=yes "$server" "echo 'OK'" >/dev/null 2>&1; then
        echo "✓ Connected"
    else
        echo "✗ Failed - may need to copy SSH key"
        echo "  Run: ./setup-ssh-keys.sh"
    fi
done

echo "=========================="
echo "Connection test complete"

