#!/bin/bash
# Check nginx status on web server (10.0.0.75)
# Can be run via SSH from dev PC OR directly on the server
# This script detects if it's running locally or remotely

set -e

# Configuration
WEB_SERVER="10.0.0.75"
WEB_SERVER_USER="vision"

# Detect if running locally on server or remotely via SSH
IS_LOCAL=false
if [ -n "$SSH_CONNECTION" ]; then
    # Running via SSH - check if we're already on the target server
    CURRENT_HOST=$(hostname 2>/dev/null || echo "")
    if echo "$CURRENT_HOST" | grep -qi "web-server\|10.0.0.75"; then
        IS_LOCAL=true
    fi
else
    # Not via SSH - check if we're on the server
    CURRENT_HOST=$(hostname 2>/dev/null || echo "")
    if echo "$CURRENT_HOST" | grep -qi "web-server\|10.0.0.75"; then
        IS_LOCAL=true
    fi
fi

# If not local, run checks via SSH
if [ "$IS_LOCAL" = false ]; then
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
    
    # Optionally try to run checks with password prompt
    echo "💡 Some checks require sudo privileges"
    echo "   You can run checks with password prompts for sudo commands"
    echo ""
    read -p "Run checks with password prompts? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "🚀 Running checks with password prompts..."
        echo ""
        # Use ssh -t to allocate pseudo-terminal for password prompts
        ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "
            # Check if nginx is installed
            if command -v nginx &> /dev/null; then
                NGINX_VERSION=\$(nginx -v 2>&1 | cut -d'/' -f2)
                echo '✅ Nginx is INSTALLED'
                echo \"   Version: \$NGINX_VERSION\"
                echo ''
                
                # Check if nginx is running
                if systemctl is-active --quiet nginx 2>/dev/null || pgrep -x nginx > /dev/null; then
                    echo '🟢 Nginx is RUNNING'
                    echo ''
                    echo '📊 Nginx processes:'
                    ps aux | grep nginx | grep -v grep | head -5
                    echo ''
                else
                    echo '🔴 Nginx is NOT RUNNING'
                    echo ''
                fi
                
                # Check nginx configuration
                if [ -d /etc/nginx ]; then
                    echo '📁 Nginx configuration directory: /etc/nginx'
                    echo ''
                    
                    # List enabled sites
                    if [ -d /etc/nginx/sites-enabled ]; then
                        ENABLED_SITES=\$(ls -1 /etc/nginx/sites-enabled/ 2>/dev/null | grep -v default || echo 'none')
                        echo '🔗 Enabled sites:'
                        echo \"\$ENABLED_SITES\" | sed 's/^/   - /'
                        echo ''
                    fi
                    
                    # Test nginx configuration (can use sudo with password prompt)
                    echo '🧪 Testing nginx configuration...'
                    if sudo nginx -t 2>&1; then
                        echo '   ✅ Configuration syntax is OK'
                        echo '   ✅ Configuration test is successful'
                    else
                        echo '   ❌ Configuration has errors (see above)'
                    fi
                    echo ''
                fi
                
                # Check nginx service status
                echo '⚙️  Systemd service status:'
                systemctl status nginx --no-pager -l 2>/dev/null | head -15 || echo '   (Unable to get service status)'
                echo ''
            else
                echo '❌ Nginx is NOT INSTALLED'
                echo ''
            fi
        " || {
            echo ""
            echo "⚠️  Remote execution completed"
            echo "   Continuing with basic checks..."
            echo ""
        }
    else
        echo ""
        echo "Running basic checks without sudo..."
        echo ""
    fi
    
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
        else
            echo "🔴 Nginx is NOT RUNNING"
            echo ""
        fi
        
        # Check nginx configuration directory
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
            echo "📝 Note: Configuration test requires sudo"
            echo "   Run script again and answer 'y' to test config with password prompt"
            echo "   Or run on server: sudo nginx -t"
        else
            echo "⚠️  Nginx is installed but NOT running"
            echo ""
            echo "📝 To start nginx:"
            echo "   ssh $WEB_SERVER_USER@$WEB_SERVER"
            echo "   sudo systemctl start nginx"
            echo ""
            echo "   Or run script again and answer 'y' to start with password prompt"
        fi
        echo ""
    else
        echo "❌ Nginx is NOT INSTALLED"
        echo ""
        echo "📝 To install nginx:"
        echo "   ./scripts/nginx/setup_nginx.sh"
        echo ""
    fi
    
    echo "=========================================="
    
else
    # Running locally on the server
    echo "=========================================="
    echo "Checking Nginx Status (Local)"
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
            sudo netstat -tlnp 2>/dev/null | grep nginx || sudo ss -tlnp 2>/dev/null | grep nginx || echo "   (Unable to check ports)"
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
            
            # Test nginx configuration (can use sudo locally)
            echo "🧪 Testing nginx configuration..."
            if sudo nginx -t 2>&1; then
                echo "   ✅ Configuration syntax is OK"
                echo "   ✅ Configuration test is successful"
            else
                echo "   ❌ Configuration has errors (see above)"
            fi
            echo ""
        fi
        
        # Check nginx service status
        echo "⚙️  Systemd service status:"
        systemctl status nginx --no-pager -l 2>/dev/null | head -15 || echo "   (Unable to get service status)"
        echo ""
        
        echo "=========================================="
        echo "SUMMARY"
        echo "=========================================="
        echo ""
        if systemctl is-active --quiet nginx 2>/dev/null || pgrep -x nginx > /dev/null; then
            echo "✅ Nginx is installed and running"
            echo ""
            echo "📝 Useful commands:"
            echo "   - Reload config: sudo systemctl reload nginx"
            echo "   - View logs: sudo tail -f /var/log/nginx/error.log"
            echo "   - Test access: curl http://localhost/docs/"
        else
            echo "⚠️  Nginx is installed but NOT running"
            echo ""
            echo "📝 To start nginx:"
            echo "   sudo systemctl start nginx"
            echo "   sudo systemctl enable nginx  # Enable on boot"
        fi
        echo ""
    else
        echo "❌ Nginx is NOT INSTALLED"
        echo ""
        echo "📝 To install nginx:"
        echo "   ./scripts/nginx/setup_nginx.sh"
        echo ""
    fi
    
    echo "=========================================="
fi
