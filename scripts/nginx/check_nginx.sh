#!/bin/bash
# Check if nginx is installed and running on the server
# This script provides information about nginx status

set -e

echo "=========================================="
echo "Checking Nginx Status"
echo "=========================================="
echo ""

# Check if nginx is installed
if command -v nginx &> /dev/null; then
    NGINX_VERSION=$(nginx -v 2>&1 | cut -d'/' -f2)
    echo "✅ Nginx is INSTALLED"
    echo "   Version: $NGINX_VERSION"
    echo ""
    
    # Check if nginx is running
    if systemctl is-active --quiet nginx 2>/dev/null || pgrep -x nginx > /dev/null; then
        echo "🟢 Nginx is RUNNING"
        echo ""
        
        # Show running processes
        echo "📊 Nginx processes:"
        ps aux | grep nginx | grep -v grep | head -5
        echo ""
        
        # Show listening ports
        echo "🔌 Listening ports:"
        netstat -tlnp 2>/dev/null | grep nginx || ss -tlnp 2>/dev/null | grep nginx || echo "   (Unable to check ports)"
        echo ""
    else
        echo "🔴 Nginx is NOT RUNNING"
        echo ""
    fi
    
    # Check nginx configuration
    if [ -d /etc/nginx ]; then
        echo "📁 Nginx configuration directory: /etc/nginx"
        echo ""
        
        # List enabled sites
        if [ -d /etc/nginx/sites-enabled ]; then
            ENABLED_SITES=$(ls -1 /etc/nginx/sites-enabled/ 2>/dev/null | grep -v default || echo "none")
            echo "🔗 Enabled sites:"
            echo "$ENABLED_SITES" | sed 's/^/   - /'
            echo ""
        fi
        
        # Check for existing docs configuration
        if [ -f /etc/nginx/sites-available/docs ] || [ -L /etc/nginx/sites-enabled/docs ]; then
            echo "⚠️  WARNING: Existing docs configuration found!"
            echo "   This will be removed during setup"
            echo ""
        fi
    fi
    
    # Check nginx service status
    if systemctl list-unit-files | grep -q nginx.service; then
        echo "⚙️  Systemd service status:"
        systemctl status nginx --no-pager -l | head -10 || true
        echo ""
    fi
    
    echo "=========================================="
    echo "RECOMMENDATION:"
    echo "=========================================="
    echo ""
    echo "The setup script will:"
    echo "   1. Stop nginx service"
    echo "   2. Remove nginx completely"
    echo "   3. Remove nginx configuration files"
    echo "   4. Reinstall nginx fresh"
    echo "   5. Configure for documentation"
    echo ""
    echo "To proceed, run:"
    echo "   sudo ~/bifrost-scripts/docs/setup_web_server.sh"
    echo ""
    
else
    echo "❌ Nginx is NOT INSTALLED"
    echo ""
    echo "The setup script will install nginx fresh."
    echo ""
    echo "To proceed, run:"
    echo "   sudo ~/bifrost-scripts/docs/setup_web_server.sh"
    echo ""
fi

echo "=========================================="

