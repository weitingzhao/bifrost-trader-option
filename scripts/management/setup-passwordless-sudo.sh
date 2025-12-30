#!/bin/bash
# Script to set up passwordless sudo on APP-SERVER
# This allows SSH commands to run sudo without password prompts

SERVER="app-server"
USER="vision"

echo "=========================================="
echo "Setting up passwordless sudo on APP-SERVER"
echo "=========================================="
echo ""
echo "This will allow the user '$USER' to run sudo commands"
echo "without a password for systemd and service management."
echo ""
echo "WARNING: This requires sudo access on APP-SERVER."
echo "You'll need to enter the sudo password once."
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Create sudoers configuration
echo ""
echo "Creating sudoers configuration..."

# Method 1: Add to sudoers.d (safer, more organized)
SUDOERS_CONTENT="$USER ALL=(ALL) NOPASSWD: /bin/systemctl, /usr/bin/journalctl, /usr/sbin/service, /usr/bin/psql, /usr/bin/createdb, /usr/bin/dropdb"

# Create a temporary script to run on the server
cat > /tmp/setup_sudoers.sh << 'SCRIPT'
#!/bin/bash
# Run this on APP-SERVER

USER="vision"
SUDOERS_FILE="/etc/sudoers.d/bifrost-management"

echo "Setting up passwordless sudo for $USER..."

# Create sudoers.d file
sudo tee "$SUDOERS_FILE" > /dev/null << 'EOF'
vision ALL=(ALL) NOPASSWD: /bin/systemctl, /usr/bin/journalctl, /usr/sbin/service, /usr/bin/psql, /usr/bin/createdb, /usr/bin/dropdb, /bin/ls, /usr/bin/lsof, /bin/netstat, /usr/bin/ss
EOF

# Set correct permissions (sudoers files must be 0440)
sudo chmod 0440 "$SUDOERS_FILE"

# Verify syntax
if sudo visudo -c -f "$SUDOERS_FILE"; then
    echo "✓ Sudoers configuration created successfully"
    echo "✓ Passwordless sudo is now enabled for systemd commands"
else
    echo "✗ Error: Invalid sudoers syntax!"
    sudo rm -f "$SUDOERS_FILE"
    exit 1
fi

echo ""
echo "Configuration file: $SUDOERS_FILE"
echo "You can now run systemctl commands without password"
SCRIPT

# Copy script to server
echo "Copying setup script to server..."
scp /tmp/setup_sudoers.sh "$SERVER:/tmp/setup_sudoers.sh"

# Run the script on server (will prompt for password once)
echo ""
echo "Running setup on server..."
echo "You'll be asked for the sudo password once:"
ssh -t "$SERVER" "bash /tmp/setup_sudoers.sh"

# Test passwordless sudo
echo ""
echo "Testing passwordless sudo..."
if ssh "$SERVER" "sudo -n systemctl --version >/dev/null 2>&1"; then
    echo "✓ Passwordless sudo is working!"
else
    echo "⚠ Passwordless sudo test failed. You may need to run the setup manually."
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "You can now run commands like:"
echo "  ssh app-server 'sudo systemctl status bifrost-api'"
echo "  ssh app-server 'sudo journalctl -u bifrost-api -n 50'"
echo ""

