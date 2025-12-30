#!/bin/bash
# Setup SSH config for easy access to servers

SSH_CONFIG="$HOME/.ssh/config"
CONFIG_ENTRY=$(cat <<'EOF'

# Bifrost Trading Servers
Host app-server
    HostName 10.0.0.80
    User vision
    IdentityFile ~/.ssh/bifrost_deploy
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

Host web-server
    HostName 10.0.0.75
    User vision
    IdentityFile ~/.ssh/bifrost_deploy
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

Host gpu-server
    HostName 10.0.0.60
    User vision
    IdentityFile ~/.ssh/bifrost_deploy
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
EOF
)

if grep -q "Bifrost Trading Servers" "$SSH_CONFIG" 2>/dev/null; then
    echo "SSH config already contains Bifrost servers"
else
    echo "$CONFIG_ENTRY" >> "$SSH_CONFIG"
    echo "SSH config updated. Added entries for app-server, web-server, gpu-server"
fi

chmod 600 "$SSH_CONFIG"
echo "SSH config permissions set"

