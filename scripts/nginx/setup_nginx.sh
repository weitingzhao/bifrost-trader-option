#!/bin/bash
# Setup nginx on web server (10.0.0.75)
# This script SSH into the server and sets up nginx for documentation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Configuration
WEB_SERVER="10.0.0.75"
WEB_SERVER_USER="vision"
DOCS_DEPLOY_PATH="/var/www/docs"
NGINX_CONFIG="/etc/nginx/sites-available/docs"

echo "=========================================="
echo "Setting up Nginx on Web Server"
echo "=========================================="
echo ""
echo "📡 Server: $WEB_SERVER_USER@$WEB_SERVER"
echo "📁 Docs path: $DOCS_DEPLOY_PATH"
echo ""

# Test SSH connection
echo "🔌 Testing SSH connection..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$WEB_SERVER_USER@$WEB_SERVER" exit 2>/dev/null; then
    echo "❌ Error: Cannot connect to $WEB_SERVER"
    echo ""
    echo "Please ensure:"
    echo "   1. Server is accessible: ping $WEB_SERVER"
    echo "   2. SSH key is configured: ssh-copy-id $WEB_SERVER_USER@$WEB_SERVER"
    echo "   3. User has SSH access"
    exit 1
fi

echo "✅ SSH connection successful"
echo ""

# Ask for sudo password once
echo "🔐 Sudo password required for nginx setup"
read -s -p "Enter sudo password: " SUDO_PASSWORD
echo ""
echo ""

# Function to execute sudo commands with password
sudo_cmd() {
    local cmd="$1"
    echo "$SUDO_PASSWORD" | ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "echo '$SUDO_PASSWORD' | sudo -S bash -c '$cmd'"
}

# Check if nginx is installed
echo "🔍 Checking current nginx status..."
NGINX_INSTALLED=$(ssh "$WEB_SERVER_USER@$WEB_SERVER" "command -v nginx 2>/dev/null" || echo "")

if [ -n "$NGINX_INSTALLED" ]; then
    NGINX_VERSION=$(ssh "$WEB_SERVER_USER@$WEB_SERVER" "nginx -v 2>&1 | cut -d'/' -f2" || echo "unknown")
    echo "⚠️  Nginx is already installed (version: $NGINX_VERSION)"
    echo ""
    echo "This script will:"
    echo "   1. Stop nginx service"
    echo "   2. Completely remove nginx"
    echo "   3. Remove nginx configuration"
    echo "   4. Reinstall nginx fresh"
    echo "   5. Configure for documentation"
    echo ""
    read -p "Continue with nginx removal and reinstall? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborted by user"
        exit 1
    fi
    
    echo ""
    echo "🛑 Stopping and removing nginx..."
    ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "SUDO_PASS='$SUDO_PASSWORD' bash -c '
        echo \"\$SUDO_PASS\" | sudo -S systemctl stop nginx 2>/dev/null || echo \"\$SUDO_PASS\" | sudo -S service nginx stop 2>/dev/null || true
        
        # Remove nginx
        if command -v apt-get &> /dev/null; then
            echo \"\$SUDO_PASS\" | sudo -S apt-get remove --purge -y nginx nginx-common nginx-core 2>/dev/null || true
            echo \"\$SUDO_PASS\" | sudo -S apt-get autoremove -y 2>/dev/null || true
            echo \"\$SUDO_PASS\" | sudo -S apt-get autoclean 2>/dev/null || true
        elif command -v yum &> /dev/null; then
            echo \"\$SUDO_PASS\" | sudo -S yum remove -y nginx 2>/dev/null || true
        elif command -v dnf &> /dev/null; then
            echo \"\$SUDO_PASS\" | sudo -S dnf remove -y nginx 2>/dev/null || true
        fi
        
        # Remove nginx configuration directories
        echo \"\$SUDO_PASS\" | sudo -S rm -rf /etc/nginx 2>/dev/null || true
        echo \"\$SUDO_PASS\" | sudo -S rm -rf /var/log/nginx 2>/dev/null || true
        echo \"\$SUDO_PASS\" | sudo -S rm -rf /var/lib/nginx 2>/dev/null || true
        
        # Kill any remaining nginx processes
        echo \"\$SUDO_PASS\" | sudo -S pkill -9 nginx 2>/dev/null || true
    '"
    
    echo "✅ Nginx removed completely"
    echo ""
fi

# Install nginx and create docs directory
echo "📦 Installing nginx and setting up directories..."
ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "SUDO_PASS='$SUDO_PASSWORD' bash -c '
    # Install nginx
    echo \"\$SUDO_PASS\" | sudo -S apt-get update
    echo \"\$SUDO_PASS\" | sudo -S apt-get install -y nginx
    
    # Create docs directory
    echo \"\$SUDO_PASS\" | sudo -S mkdir -p $DOCS_DEPLOY_PATH
    echo \"\$SUDO_PASS\" | sudo -S chown -R www-data:www-data $DOCS_DEPLOY_PATH
    echo \"\$SUDO_PASS\" | sudo -S chmod -R 755 $DOCS_DEPLOY_PATH
'"

# Deploy nginx configurations
echo "⚙️  Deploying nginx configurations..."

# Deploy nginx_docs.conf
if [ -f "$SCRIPT_DIR/nginx_docs.conf" ]; then
    echo "   📋 Deploying nginx_docs.conf..."
    scp "$SCRIPT_DIR/nginx_docs.conf" "$WEB_SERVER_USER@$WEB_SERVER:/tmp/nginx_docs.conf"
fi

# Deploy bifrost.conf if available
if [ -f "$SCRIPT_DIR/bifrost.conf" ]; then
    echo "   📋 Preparing bifrost.conf..."
    scp "$SCRIPT_DIR/bifrost.conf" "$WEB_SERVER_USER@$WEB_SERVER:/tmp/bifrost.conf"
fi

# Deploy all configs in one SSH session
if [ -f "$SCRIPT_DIR/nginx_docs.conf" ]; then
    ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "SUDO_PASS='$SUDO_PASSWORD' bash -c '
        # Deploy nginx_docs.conf
        echo \"\$SUDO_PASS\" | sudo -S cp /tmp/nginx_docs.conf $NGINX_CONFIG
        echo \"\$SUDO_PASS\" | sudo -S chmod 644 $NGINX_CONFIG
        rm /tmp/nginx_docs.conf
        echo \"✅ nginx_docs.conf deployed\"
        
        # Deploy bifrost.conf if available
        if [ -f /tmp/bifrost.conf ]; then
            echo \"\$SUDO_PASS\" | sudo -S cp /tmp/bifrost.conf /etc/nginx/sites-available/bifrost
            echo \"\$SUDO_PASS\" | sudo -S chmod 644 /etc/nginx/sites-available/bifrost
            rm /tmp/bifrost.conf
            echo \"✅ bifrost.conf deployed (not enabled by default)\"
        fi
    '"
else
    echo "   ⚠️  Warning: nginx_docs.conf not found, creating inline..."
    ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "SUDO_PASS='$SUDO_PASSWORD' bash -c 'echo \"\$SUDO_PASS\" | sudo -S tee $NGINX_CONFIG > /dev/null'" << 'EOF'
server {
    listen 80;
    server_name 10.0.0.75;
    
    location = /docs {
        return 301 /docs/;
    }
    
    location /docs/ {
        alias /var/www/docs/;
        index index.html index.htm;
        try_files $uri $uri/ /docs/index.html;
        
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
        
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }
    
    location = / {
        return 301 /docs/;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
    ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "SUDO_PASS='$SUDO_PASSWORD' bash -c 'echo \"\$SUDO_PASS\" | sudo -S chmod 644 $NGINX_CONFIG'"
fi

# Enable site, test config, and start nginx (all in one session)
echo "🔗 Enabling site, testing config, and starting nginx..."
ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "SUDO_PASS='$SUDO_PASSWORD' bash -c '
    # Remove default site if it exists
    if [ -L /etc/nginx/sites-enabled/default ]; then
        echo \"\$SUDO_PASS\" | sudo -S rm /etc/nginx/sites-enabled/default
        echo \"✅ Removed default site\"
    fi
    
    # Enable docs site
    if [ ! -L /etc/nginx/sites-enabled/docs ]; then
        echo \"\$SUDO_PASS\" | sudo -S ln -s $NGINX_CONFIG /etc/nginx/sites-enabled/
        echo \"✅ Docs site enabled\"
    else
        # Remove old symlink and create new one to ensure it points to correct config
        echo \"\$SUDO_PASS\" | sudo -S rm /etc/nginx/sites-enabled/docs
        echo \"\$SUDO_PASS\" | sudo -S ln -s $NGINX_CONFIG /etc/nginx/sites-enabled/
        echo \"✅ Docs site re-enabled with latest config\"
    fi
    
    # Disable bifrost site if it exists (to avoid conflicts)
    if [ -L /etc/nginx/sites-enabled/bifrost ]; then
        echo \"\$SUDO_PASS\" | sudo -S rm /etc/nginx/sites-enabled/bifrost
        echo \"⚠️  Bifrost site disabled (can be enabled later if needed)\"
    fi
    
    # Test nginx configuration
    echo \"\"
    echo \"🧪 Testing nginx configuration...\"
    if echo \"\$SUDO_PASS\" | sudo -S nginx -t; then
        echo \"✅ Nginx configuration is valid\"
    else
        echo \"❌ Error: Nginx configuration test failed\"
        exit 1
    fi
    
    # Start/reload nginx
    echo \"\"
    echo \"🔄 Starting nginx...\"
    echo \"\$SUDO_PASS\" | sudo -S systemctl enable nginx
    echo \"\$SUDO_PASS\" | sudo -S systemctl start nginx
    echo \"\$SUDO_PASS\" | sudo -S systemctl reload nginx 2>/dev/null || true
    echo \"✅ Nginx started and enabled\"
'"

# Verify nginx is running
echo "🔍 Verifying nginx is running..."
if ssh "$WEB_SERVER_USER@$WEB_SERVER" "systemctl is-active --quiet nginx"; then
    echo "✅ Nginx is running"
else
    echo "⚠️  Warning: Nginx may not be running. Check manually:"
    echo "   ssh $WEB_SERVER_USER@$WEB_SERVER 'sudo systemctl status nginx'"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📖 Documentation will be available at:"
echo "   http://$WEB_SERVER/docs/"
echo ""
echo "📝 Next steps:"
echo "   1. Deploy documentation from dev PC:"
echo "      ./scripts/docs/deploy_docs.sh"
echo ""
echo "   2. Test access:"
echo "      curl http://$WEB_SERVER/docs/"
echo ""
echo "   3. Check nginx status:"
echo "      ./scripts/nginx/check_nginx.sh"
echo ""

