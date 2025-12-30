# Management Scripts

This directory contains scripts for managing and deploying the Bifrost Options Trading Strategy Analyzer across multiple servers.

## Quick Start

### 1. Initial Setup (One-time)

```bash
# Set up SSH config
./ssh-config.sh

# Copy SSH keys to all servers (requires password for first time)
./setup-ssh-keys.sh

# Test connections
./test-connections.sh
```

### 2. Deploy Code

```bash
# Deploy to APP-SERVER
./deploy-app-server.sh

# Or manually sync files
rsync -avz --exclude='.git' --exclude='venv' \
    ../.. app-server:~/bifrost-trader/
```

## Available Scripts

- **`ssh-config.sh`**: Set up SSH config for easy server access
- **`setup-ssh-keys.sh`**: Copy SSH public key to all servers
- **`test-connections.sh`**: Test SSH connections to all servers
- **`deploy-app-server.sh`**: Deploy code to APP-SERVER
- **`servers.conf`**: Server configuration file

## Manual Deployment Steps

Since some operations require sudo access, see [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for complete manual deployment instructions.

## Server Access

After running `ssh-config.sh`, you can access servers directly:

```bash
ssh app-server    # Connect to APP-SERVER (10.0.0.80)
ssh web-server    # Connect to Web-Server (10.0.0.75)
ssh gpu-server    # Connect to RTX4090-Server (10.0.0.60)
```

## Current Status

✅ SSH configuration complete
✅ SSH keys set up
✅ Code synced to APP-SERVER
⏳ System dependencies need to be installed (requires sudo)
⏳ Python environment setup needed
⏳ Database setup needed
⏳ IB Gateway installation needed
⏳ Systemd services configuration needed

## Next Steps

1. **On APP-SERVER**, run with sudo:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3 python3-pip python3-venv postgresql postgresql-contrib
   ```

2. **Set up Python environment**:
   ```bash
   cd ~/bifrost-trader
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Follow the complete guide**: See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

