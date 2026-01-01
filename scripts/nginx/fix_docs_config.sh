#!/bin/bash
# Fix nginx docs configuration and deploy documentation
# This script sets up nginx config for docs and deploys the documentation

# Configuration
WEB_SERVER="10.0.0.75"
WEB_SERVER_USER="vision"
DOCS_DEPLOY_PATH="/var/www/docs"
NGINX_CONFIG="/etc/nginx/sites-available/docs"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Detect if running locally on server or remotely via SSH
IS_LOCAL=false
if [ -n "$SSH_CONNECTION" ]; then
    CURRENT_HOST=$(hostname 2>/dev/null || echo "")
    if echo "$CURRENT_HOST" | grep -qi "web-server\|10.0.0.75"; then
        IS_LOCAL=true
    fi
else
    CURRENT_HOST=$(hostname 2>/dev/null || echo "")
    if echo "$CURRENT_HOST" | grep -qi "web-server\|10.0.0.75"; then
        IS_LOCAL=true
    fi
fi

# If not local, run via SSH with password prompt
if [ "$IS_LOCAL" = false ]; then
    echo "=========================================="
    echo "Fixing Nginx Docs Configuration"
    echo "=========================================="
    echo ""
    echo "📡 Server: $WEB_SERVER_USER@$WEB_SERVER"
    echo ""
    
    # Test SSH connection
    if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$WEB_SERVER_USER@$WEB_SERVER" exit 2>/dev/null; then
        echo "❌ Error: Cannot connect to $WEB_SERVER"
        exit 1
    fi
    
    echo "✅ SSH connection successful"
    echo ""
    echo "🚀 Setting up nginx docs configuration with password prompt..."
    echo ""
    
    # Copy nginx config to server
    echo "📋 Copying nginx docs configuration..."
    scp "$SCRIPT_DIR/nginx_docs.conf" "$WEB_SERVER_USER@$WEB_SERVER:/tmp/nginx_docs.conf"
    
    # Use ssh -t to allocate pseudo-terminal for password prompts
    ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "
        # Copy config to nginx directory
        sudo cp /tmp/nginx_docs.conf $NGINX_CONFIG
        sudo rm /tmp/nginx_docs.conf
        
        # Enable site
        if [ ! -L /etc/nginx/sites-enabled/docs ]; then
            sudo ln -s $NGINX_CONFIG /etc/nginx/sites-enabled/
            echo '✅ Docs site enabled'
        else
            echo '✅ Docs site already enabled'
        fi
        
        # Test configuration
        echo ''
        echo '🧪 Testing nginx configuration...'
        if sudo nginx -t 2>&1; then
            echo '✅ Configuration is valid'
            echo ''
            echo '🔄 Reloading nginx...'
            sudo systemctl reload nginx
            echo '✅ Nginx reloaded'
        else
            echo '❌ Configuration has errors'
            exit 1
        fi
    " || {
        echo ""
        echo "⚠️  Could not setup nginx config remotely"
        echo "   Please SSH into server and run manually"
        exit 1
    }
    
    echo ""
    echo "✅ Nginx docs configuration setup complete!"
    echo ""
    echo "📝 Next: Deploy documentation files"
    echo "   Run: ./scripts/docs/deploy_docs.sh"
    echo ""
    
else
    # Running locally on the server
    echo "=========================================="
    echo "Fixing Nginx Docs Configuration (Local)"
    echo "=========================================="
    echo ""
    
    # Copy config
    if [ -f "$SCRIPT_DIR/nginx_docs.conf" ]; then
        echo "📋 Copying nginx docs configuration..."
        sudo cp "$SCRIPT_DIR/nginx_docs.conf" "$NGINX_CONFIG"
        echo "✅ Config copied"
    else
        echo "❌ Error: nginx_docs.conf not found at $SCRIPT_DIR/nginx_docs.conf"
        exit 1
    fi
    
    # Enable site
    echo "🔗 Enabling docs site..."
    if [ ! -L /etc/nginx/sites-enabled/docs ]; then
        sudo ln -s "$NGINX_CONFIG" /etc/nginx/sites-enabled/
        echo "✅ Docs site enabled"
    else
        echo "✅ Docs site already enabled"
    fi
    
    # Test configuration
    echo ""
    echo "🧪 Testing nginx configuration..."
    if sudo nginx -t 2>&1; then
        echo "✅ Configuration is valid"
        echo ""
        echo "🔄 Reloading nginx..."
        sudo systemctl reload nginx
        echo "✅ Nginx reloaded"
    else
        echo "❌ Configuration has errors"
        exit 1
    fi
    
    echo ""
    echo "✅ Nginx docs configuration setup complete!"
    echo ""
fi

echo "=========================================="

