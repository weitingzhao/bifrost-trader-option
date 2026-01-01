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
    echo "🛑 Stopping nginx service..."
    echo "💡 This requires sudo privileges (will prompt for password)"
    ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "
        sudo systemctl stop nginx 2>/dev/null || sudo service nginx stop 2>/dev/null || true
    "
    
    echo "🗑️  Removing nginx..."
    echo "💡 This requires sudo privileges (will prompt for password)"
    ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "
        if command -v apt-get &> /dev/null; then
            sudo apt-get remove --purge -y nginx nginx-common nginx-core 2>/dev/null || true
            sudo apt-get autoremove -y 2>/dev/null || true
            sudo apt-get autoclean 2>/dev/null || true
        elif command -v yum &> /dev/null; then
            sudo yum remove -y nginx 2>/dev/null || true
        elif command -v dnf &> /dev/null; then
            sudo dnf remove -y nginx 2>/dev/null || true
        fi
        
        # Remove nginx configuration directories
        sudo rm -rf /etc/nginx 2>/dev/null || true
        sudo rm -rf /var/log/nginx 2>/dev/null || true
        sudo rm -rf /var/lib/nginx 2>/dev/null || true
        
        # Kill any remaining nginx processes
        sudo pkill -9 nginx 2>/dev/null || true
    "
    
    echo "✅ Nginx removed completely"
    echo ""
fi

# Install nginx fresh
echo "📦 Installing nginx..."
echo "💡 This requires sudo privileges (will prompt for password)"
ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "
    sudo apt-get update
    sudo apt-get install -y nginx
"

# Create docs directory
echo "📁 Creating documentation directory..."
echo "💡 This requires sudo privileges (will prompt for password)"
ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "
    sudo mkdir -p $DOCS_DEPLOY_PATH
    sudo chown -R www-data:www-data $DOCS_DEPLOY_PATH
    sudo chmod -R 755 $DOCS_DEPLOY_PATH
"

# Deploy nginx configurations
echo "⚙️  Deploying nginx configurations..."
echo "💡 This requires sudo (will prompt for password)"

# Deploy nginx_docs.conf
if [ -f "$SCRIPT_DIR/nginx_docs.conf" ]; then
    echo "   📋 Deploying nginx_docs.conf..."
    scp "$SCRIPT_DIR/nginx_docs.conf" "$WEB_SERVER_USER@$WEB_SERVER:/tmp/nginx_docs.conf"
    ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "
        sudo cp /tmp/nginx_docs.conf $NGINX_CONFIG
        sudo chmod 644 $NGINX_CONFIG
        rm /tmp/nginx_docs.conf
        echo '✅ nginx_docs.conf deployed'
    "
else
    echo "   ⚠️  Warning: nginx_docs.conf not found, creating inline..."
    ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "sudo tee $NGINX_CONFIG > /dev/null" << 'EOF'
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
    ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "sudo chmod 644 $NGINX_CONFIG"
fi

# Deploy bifrost.conf (optional, for future use)
if [ -f "$SCRIPT_DIR/bifrost.conf" ]; then
    echo "   📋 Deploying bifrost.conf..."
    scp "$SCRIPT_DIR/bifrost.conf" "$WEB_SERVER_USER@$WEB_SERVER:/tmp/bifrost.conf"
    ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "
        sudo cp /tmp/bifrost.conf /etc/nginx/sites-available/bifrost
        sudo chmod 644 /etc/nginx/sites-available/bifrost
        rm /tmp/bifrost.conf
        echo '✅ bifrost.conf deployed (not enabled by default)'
    "
fi

# Enable site and remove conflicting configs
echo "🔗 Enabling nginx site..."
echo "💡 This requires sudo (will prompt for password)"
ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "
    # Remove default site if it exists
    if [ -L /etc/nginx/sites-enabled/default ]; then
        sudo rm /etc/nginx/sites-enabled/default
        echo '✅ Removed default site'
    fi
    
    # Enable docs site
    if [ ! -L /etc/nginx/sites-enabled/docs ]; then
        sudo ln -s $NGINX_CONFIG /etc/nginx/sites-enabled/
        echo '✅ Docs site enabled'
    else
        # Remove old symlink and create new one to ensure it points to correct config
        sudo rm /etc/nginx/sites-enabled/docs
        sudo ln -s $NGINX_CONFIG /etc/nginx/sites-enabled/
        echo '✅ Docs site re-enabled with latest config'
    fi
    
    # Disable bifrost site if it exists (to avoid conflicts)
    if [ -L /etc/nginx/sites-enabled/bifrost ]; then
        sudo rm /etc/nginx/sites-enabled/bifrost
        echo '⚠️  Bifrost site disabled (can be enabled later if needed)'
    fi
"

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
echo "💡 This requires sudo (will prompt for password)"
if ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "sudo nginx -t"; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Error: Nginx configuration test failed"
    exit 1
fi

# Start/reload nginx
echo "🔄 Starting nginx..."
echo "💡 This requires sudo (will prompt for password)"
ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "
    sudo systemctl enable nginx
    sudo systemctl start nginx
    sudo systemctl reload nginx 2>/dev/null || true
    echo '✅ Nginx started and enabled'
"

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

