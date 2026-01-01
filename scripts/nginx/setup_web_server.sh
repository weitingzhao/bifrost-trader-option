#!/bin/bash
# Setup nginx on web server (10.0.0.75) to serve MkDocs documentation
# Run this script on the web server (10.0.0.75)
# This script will completely remove and reinstall nginx if it exists

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
WEB_SERVER="10.0.0.75"
DOCS_DEPLOY_PATH="/var/www/docs"
NGINX_CONFIG="/etc/nginx/sites-available/docs"

echo "=========================================="
echo "Setting up Nginx for Documentation"
echo "=========================================="
echo ""
echo "📡 Server: $WEB_SERVER"
echo "📁 Docs path: $DOCS_DEPLOY_PATH"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Error: This script must be run as root (use sudo)"
    exit 1
fi

# Check if nginx is installed
if command -v nginx &> /dev/null; then
    NGINX_VERSION=$(nginx -v 2>&1 | cut -d'/' -f2)
    echo "⚠️  Nginx is already installed (version: $NGINX_VERSION)"
    echo ""
    echo "This script will:"
    echo "   1. Stop nginx service"
    echo "   2. Completely remove nginx"
    echo "   3. Remove nginx configuration"
    echo "   4. Reinstall nginx fresh"
    echo ""
    read -p "Continue with nginx removal and reinstall? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborted by user"
        exit 1
    fi
    
    echo ""
    echo "🛑 Stopping nginx service..."
    systemctl stop nginx 2>/dev/null || service nginx stop 2>/dev/null || true
    
    echo "🗑️  Removing nginx..."
    # Remove nginx completely
    if command -v apt-get &> /dev/null; then
        apt-get remove --purge -y nginx nginx-common nginx-core 2>/dev/null || true
        apt-get autoremove -y 2>/dev/null || true
        apt-get autoclean 2>/dev/null || true
    elif command -v yum &> /dev/null; then
        yum remove -y nginx 2>/dev/null || true
    elif command -v dnf &> /dev/null; then
        dnf remove -y nginx 2>/dev/null || true
    fi
    
    # Remove nginx configuration directories
    echo "🧹 Cleaning up nginx configuration..."
    rm -rf /etc/nginx 2>/dev/null || true
    rm -rf /var/log/nginx 2>/dev/null || true
    rm -rf /var/lib/nginx 2>/dev/null || true
    
    # Kill any remaining nginx processes
    pkill -9 nginx 2>/dev/null || true
    
    echo "✅ Nginx removed completely"
    echo ""
fi

# Install nginx fresh
echo "📦 Installing nginx fresh..."
apt-get update
apt-get install -y nginx

# Create docs directory
echo "📁 Creating documentation directory..."
mkdir -p "$DOCS_DEPLOY_PATH"
chown -R www-data:www-data "$DOCS_DEPLOY_PATH"
chmod -R 755 "$DOCS_DEPLOY_PATH"

# Create nginx configuration
echo "⚙️  Creating nginx configuration..."
# Use template from scripts/nginx/ if available, otherwise create inline
if [ -f "$SCRIPT_DIR/../nginx/nginx_docs.conf" ]; then
    cp "$SCRIPT_DIR/../nginx/nginx_docs.conf" "$NGINX_CONFIG"
else
    # Fallback: create configuration inline
    cat > "$NGINX_CONFIG" << 'EOF'
server {
    listen 80;
    server_name 10.0.0.75;
    
    location /docs/ {
        alias /var/www/docs/;
        index index.html;
        try_files $uri $uri/ =404;
        
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

# Enable site
echo "🔗 Enabling nginx site..."
if [ -L /etc/nginx/sites-enabled/docs ]; then
    echo "   Site already enabled"
else
    ln -s "$NGINX_CONFIG" /etc/nginx/sites-enabled/
fi

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
if nginx -t; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Error: Nginx configuration test failed"
    exit 1
fi

# Reload nginx
echo "🔄 Reloading nginx..."
systemctl reload nginx

# Check nginx status
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx is running"
else
    echo "⚠️  Warning: Nginx is not running. Starting..."
    systemctl start nginx
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

