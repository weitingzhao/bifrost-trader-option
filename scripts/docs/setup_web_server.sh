#!/bin/bash
# Setup nginx on web server (10.0.0.75) to serve MkDocs documentation
# Run this script on the web server (10.0.0.75)

set -e

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
if ! command -v nginx &> /dev/null; then
    echo "📦 Installing nginx..."
    apt-get update
    apt-get install -y nginx
fi

# Create docs directory
echo "📁 Creating documentation directory..."
mkdir -p "$DOCS_DEPLOY_PATH"
chown -R www-data:www-data "$DOCS_DEPLOY_PATH"
chmod -R 755 "$DOCS_DEPLOY_PATH"

# Create nginx configuration
echo "⚙️  Creating nginx configuration..."
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

