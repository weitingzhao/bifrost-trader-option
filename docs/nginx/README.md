# Nginx Configuration and Management

This directory contains all nginx-related documentation for the Bifrost project.

## Overview

Nginx is used on the Web-Server (10.0.0.75) to serve:
- Static documentation (MkDocs)
- Frontend application (React/Vue)
- Reverse proxy to FastAPI and Django backends
- WebSocket connections for real-time updates

## Files

### Configuration Files
- **[nginx_docs.conf](../scripts/nginx/nginx_docs.conf)** - Nginx configuration for documentation server
- **[bifrost.conf](../scripts/nginx/bifrost.conf)** - Main nginx configuration for Bifrost services

### Documentation
- **[SETUP.md](SETUP.md)** - Nginx setup and installation guide
- **[CONFIGURATION.md](CONFIGURATION.md)** - Detailed configuration reference

## Quick Start

### Initial Setup

1. **Copy nginx setup scripts to server:**
   ```bash
   ./scripts/nginx/copy_setup_to_server.sh
   ```

2. **Check nginx status:**
   ```bash
   ssh vision@10.0.0.75
   ~/bifrost-scripts/nginx/check_nginx.sh
   ```

3. **Run setup:**
   ```bash
   sudo ~/bifrost-scripts/nginx/setup_nginx.sh
   ```

### Configuration Locations

- **Server config**: `/etc/nginx/sites-available/`
- **Enabled sites**: `/etc/nginx/sites-enabled/`
- **Main config**: `/etc/nginx/nginx.conf`
- **Logs**: `/var/log/nginx/`

## Services

### Documentation Server
- **URL**: `http://10.0.0.75/docs/`
- **Config**: `nginx_docs.conf`
- **Document Root**: `/var/www/docs/`

### Main Application
- **URL**: `http://10.0.0.75/`
- **Config**: `bifrost.conf`
- **Frontend**: `/opt/bifrost-frontend/build`
- **API Proxy**: `10.0.0.80:8000` (FastAPI)
- **Admin Proxy**: `10.0.0.80:8001` (Django)

## Management

### Reload Configuration
```bash
sudo nginx -t  # Test configuration
sudo systemctl reload nginx  # Reload without downtime
```

### Restart Nginx
```bash
sudo systemctl restart nginx
```

### Check Status
```bash
sudo systemctl status nginx
```

### View Logs
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## Troubleshooting

### Configuration Test
```bash
sudo nginx -t
```

### Check Listening Ports
```bash
sudo netstat -tlnp | grep nginx
# or
sudo ss -tlnp | grep nginx
```

### Check Process Status
```bash
ps aux | grep nginx
```

### Common Issues

1. **Port already in use**: Check what's using port 80/443
2. **Permission denied**: Ensure nginx user has access to document root
3. **502 Bad Gateway**: Check backend services are running
4. **403 Forbidden**: Check file permissions and SELinux (if enabled)

## Related Documentation

- [Documentation Deployment](../DEPLOYMENT.md) - Deploying MkDocs to web server
- [Project Plan](../PROJECT_PLAN.md) - Overall architecture
- [Setup Guide](../setup/NEXT_STEPS.md) - Initial project setup

