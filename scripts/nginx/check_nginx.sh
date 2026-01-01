#!/bin/bash
# Check nginx status on web server (10.0.0.75)
# This script SSH into the server and checks if nginx is installed and running

set -e

# Configuration
WEB_SERVER="10.0.0.75"
WEB_SERVER_USER="vision"

echo "=========================================="
echo "Checking Nginx Status on Web Server"
echo "=========================================="
echo ""
echo "📡 Server: $WEB_SERVER_USER@$WEB_SERVER"
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
echo "🔍 Checking nginx installation..."
NGINX_INSTALLED=$(ssh "$WEB_SERVER_USER@$WEB_SERVER" "command -v nginx 2>/dev/null" || echo "")

if [ -n "$NGINX_INSTALLED" ]; then
    NGINX_VERSION=$(ssh "$WEB_SERVER_USER@$WEB_SERVER" "nginx -v 2>&1 | cut -d'/' -f2" || echo "unknown")
    echo "✅ Nginx is INSTALLED"
    echo "   Version: $NGINX_VERSION"
    echo "   Path: $NGINX_INSTALLED"
    echo ""
    
    # Check if nginx is running
    echo "🔍 Checking nginx service status..."
    NGINX_RUNNING=$(ssh "$WEB_SERVER_USER@$WEB_SERVER" "systemctl is-active nginx 2>/dev/null || pgrep -x nginx > /dev/null && echo 'running' || echo 'stopped'" || echo "unknown")
    
    if [ "$NGINX_RUNNING" = "running" ] || [ "$NGINX_RUNNING" = "active" ]; then
        echo "🟢 Nginx is RUNNING"
        echo ""
        
        # Show running processes
        echo "📊 Nginx processes:"
        ssh "$WEB_SERVER_USER@$WEB_SERVER" "ps aux | grep nginx | grep -v grep | head -5" || echo "   (Unable to get process list)"
        echo ""
        
        # Show listening ports
        echo "🔌 Listening ports:"
        ssh "$WEB_SERVER_USER@$WEB_SERVER" "sudo netstat -tlnp 2>/dev/null | grep nginx || sudo ss -tlnp 2>/dev/null | grep nginx || echo '   (Unable to check ports - may need sudo)'" || echo "   (Unable to check ports)"
        echo ""
    else
        echo "🔴 Nginx is NOT RUNNING"
        echo ""
        echo "⚠️  To start nginx:"
        echo "   ssh $WEB_SERVER_USER@$WEB_SERVER"
        echo "   sudo systemctl start nginx"
        echo ""
    fi
    
    # Check nginx configuration
    echo "📁 Checking nginx configuration..."
    if ssh "$WEB_SERVER_USER@$WEB_SERVER" "[ -d /etc/nginx ]" 2>/dev/null; then
        echo "   Configuration directory: /etc/nginx"
        echo ""
        
        # List enabled sites
        if ssh "$WEB_SERVER_USER@$WEB_SERVER" "[ -d /etc/nginx/sites-enabled ]" 2>/dev/null; then
            ENABLED_SITES=$(ssh "$WEB_SERVER_USER@$WEB_SERVER" "ls -1 /etc/nginx/sites-enabled/ 2>/dev/null | grep -v default || echo 'none'")
            echo "🔗 Enabled sites:"
            echo "$ENABLED_SITES" | sed 's/^/   - /'
            echo ""
        fi
        
        # Check for docs configuration
        if ssh "$WEB_SERVER_USER@$WEB_SERVER" "[ -f /etc/nginx/sites-available/docs ] || [ -L /etc/nginx/sites-enabled/docs ]" 2>/dev/null; then
            echo "✅ Documentation site configuration found"
            echo ""
        else
            echo "⚠️  Documentation site configuration NOT found"
            echo ""
        fi
        
        # Test nginx configuration (if sudo is available without password)
        echo "🧪 Testing nginx configuration..."
        CONFIG_TEST=$(ssh "$WEB_SERVER_USER@$WEB_SERVER" "sudo -n nginx -t 2>&1" 2>/dev/null || echo "")
        if [ -z "$CONFIG_TEST" ]; then
            echo "   ⚠️  Cannot test configuration (sudo requires password)"
            echo "   To test manually: ssh $WEB_SERVER_USER@$WEB_SERVER 'sudo nginx -t'"
        elif echo "$CONFIG_TEST" | grep -q "syntax is ok"; then
            echo "   ✅ Configuration syntax is OK"
            if echo "$CONFIG_TEST" | grep -q "test is successful"; then
                echo "   ✅ Configuration test is successful"
            fi
        else
            echo "   ❌ Configuration has errors:"
            echo "$CONFIG_TEST" | sed 's/^/      /'
        fi
        echo ""
    fi
    
    # Check nginx service status
    echo "⚙️  Systemd service status:"
    ssh "$WEB_SERVER_USER@$WEB_SERVER" "systemctl status nginx --no-pager -l 2>/dev/null | head -15" || echo "   (Unable to get service status)"
    echo ""
    
    echo "=========================================="
    echo "SUMMARY"
    echo "=========================================="
    echo ""
    if [ "$NGINX_RUNNING" = "running" ] || [ "$NGINX_RUNNING" = "active" ]; then
        echo "✅ Nginx is installed and running"
        echo ""
        echo "📝 Next steps:"
        echo "   - Test access: curl http://$WEB_SERVER/docs/"
        echo "   - View logs: ssh $WEB_SERVER_USER@$WEB_SERVER 'sudo tail -f /var/log/nginx/error.log'"
        echo "   - Reload config: ssh $WEB_SERVER_USER@$WEB_SERVER 'sudo systemctl reload nginx'"
    else
        echo "⚠️  Nginx is installed but NOT running"
        echo ""
        echo "📝 To start nginx:"
        echo "   ssh $WEB_SERVER_USER@$WEB_SERVER"
        echo "   sudo systemctl start nginx"
        echo "   sudo systemctl enable nginx  # Enable on boot"
    fi
    echo ""
    
else
    echo "❌ Nginx is NOT INSTALLED"
    echo ""
    echo "📝 To install and setup nginx:"
    echo ""
    echo "   1. Copy setup scripts to server:"
    echo "      ./scripts/nginx/copy_setup_to_server.sh"
    echo ""
    echo "   2. SSH into server and run setup:"
    echo "      ssh $WEB_SERVER_USER@$WEB_SERVER"
    echo "      sudo ~/bifrost-scripts/nginx/setup_web_server.sh"
    echo ""
fi

echo "=========================================="
