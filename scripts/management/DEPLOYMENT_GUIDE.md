# Deployment Guide

This guide provides step-by-step instructions for deploying the Bifrost Options Trading Strategy Analyzer to all servers.

## Prerequisites

1. SSH access to all servers (already configured)
2. Sudo access on all servers (for installing system packages)

## APP-SERVER (10.0.0.80) Deployment

### Step 1: Install System Dependencies

```bash
ssh app-server
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv postgresql postgresql-contrib
```

### Step 2: Set Up Python Environment

```bash
cd ~/bifrost-trader
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
cd ~/bifrost-trader
cat > .env << 'EOF'
IB_HOST=127.0.0.1
IB_PORT=7497
IB_CLIENT_ID=1
DATABASE_URL=postgresql://bifrost:changeme@localhost:5432/options_db
ML_API_URL=http://10.0.0.60:8001
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=False
OPTIONS_CACHE_TTL=60
EOF
```

### Step 4: Set Up PostgreSQL Database

```bash
sudo -u postgres psql << 'EOF'
CREATE USER bifrost WITH PASSWORD 'changeme';
CREATE DATABASE options_db OWNER bifrost;
\q
EOF

# Install TimescaleDB extension (if available)
sudo -u postgres psql -d options_db -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
```

### Step 5: Install IB Gateway (Headless)

1. Download IB Gateway from Interactive Brokers website
2. Extract to `/opt/ibgateway` or `~/ibgateway`
3. Configure for headless operation
4. Set up systemd service (see below)

### Step 6: Create Systemd Services

Create `/etc/systemd/system/bifrost-api.service`:

```ini
[Unit]
Description=Bifrost Options Trading API
After=network.target postgresql.service

[Service]
Type=simple
User=vision
WorkingDirectory=/home/vision/bifrost-trader
Environment="PATH=/home/vision/bifrost-trader/venv/bin"
ExecStart=/home/vision/bifrost-trader/venv/bin/python -m src.main
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable bifrost-api
sudo systemctl start bifrost-api
sudo systemctl status bifrost-api
```

## Web-Server (10.0.0.75) Deployment

### Step 1: Install Nginx

```bash
ssh web-server
sudo apt-get update
sudo apt-get install -y nginx
```

### Step 2: Configure Nginx

Create `/etc/nginx/sites-available/bifrost`:

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://10.0.0.80:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://10.0.0.80:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/bifrost /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## RTX4090-Server (10.0.0.60) Deployment

### Step 1: Install ML Dependencies

```bash
ssh gpu-server
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# Install CUDA and GPU drivers (if not already installed)
# Follow NVIDIA CUDA installation guide for your system
```

### Step 2: Set Up Python Environment

```bash
cd ~/bifrost-trader  # or create separate ML service directory
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install fastapi uvicorn psycopg2-binary sqlalchemy
```

### Step 3: Configure Environment

```bash
cat > .env << 'EOF'
DATABASE_URL=postgresql://bifrost:changeme@10.0.0.80:5432/options_db
ML_API_HOST=0.0.0.0
ML_API_PORT=8001
GPU_DEVICE=0
MODEL_PATH=/home/vision/bifrost-ml/models
EOF
```

## Verification

### Test APP-SERVER

```bash
ssh app-server
cd ~/bifrost-trader
source venv/bin/activate
python -m src.main
# Should start FastAPI server on port 8000
```

### Test Web-Server

```bash
curl http://10.0.0.75/api/health
```

### Test All Services

From Dev PC, run:

```bash
./scripts/management/health-check.sh all
```

## Next Steps

1. Configure IB Gateway credentials
2. Set up database schema for option history
3. Configure firewall rules
4. Set up automated backups
5. Configure monitoring and alerts

