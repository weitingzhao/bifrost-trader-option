#!/bin/bash
# Copy SSH keys to all servers

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/servers.conf"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: servers.conf not found at $CONFIG_FILE"
    exit 1
fi

# Read server configs
declare -A servers
while IFS='=' read -r key value; do
    if [[ $key =~ ^\[(.+)\]$ ]]; then
        current_section="${BASH_REMATCH[1]}"
    elif [[ -n $current_section && -n $key && -n $value ]]; then
        servers["${current_section}_${key}"]="$value"
    fi
done < "$CONFIG_FILE"

# Extract server names
server_names=("app-server" "web-server" "gpu-server")

PUBLIC_KEY="$HOME/.ssh/bifrost_deploy.pub"

if [ ! -f "$PUBLIC_KEY" ]; then
    echo "Error: SSH public key not found at $PUBLIC_KEY"
    echo "Please run: ssh-keygen -t rsa -b 4096 -f ~/.ssh/bifrost_deploy"
    exit 1
fi

echo "Copying SSH key to servers..."
for server in "${server_names[@]}"; do
    host_key="${server}_host"
    user_key="${server}_user"
    host="${servers[$host_key]}"
    user="${servers[$user_key]}"
    
    if [ -z "$host" ] || [ -z "$user" ]; then
        echo "Warning: Missing config for $server, skipping..."
        continue
    fi
    
    echo "Copying key to $user@$host..."
    ssh-copy-id -i "$PUBLIC_KEY" "$user@$host" 2>&1 | grep -v "attempting to log in" || echo "Key may already be installed or connection failed"
done

echo "SSH key setup complete!"

