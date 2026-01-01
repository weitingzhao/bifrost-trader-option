# Nginx Setup Guide

Complete guide for setting up and configuring nginx on the Web-Server (10.0.0.75).

## Prerequisites

- Ubuntu/Debian Linux server
- Root or sudo access
- Port 80 (and optionally 443) open in firewall

## Installation

### Automated Setup

The easiest way is to use the provided setup script:

```bash
# From dev PC: Copy nginx setup scripts to server
./scripts/nginx/copy_setup_to_server.sh

# SSH into server
ssh vision@10.0.0.75

# Check nginx status (optional)
~/bifrost-scripts/nginx/check_nginx.sh

# Run setup (will handle existing nginx)
sudo ~/bifrost-scripts/nginx/setup_web_server.sh
```

### Manual Installation

If you prefer manual setup:

```bash
# Update package list
sudo apt-get update

# Install nginx
sudo apt-get install -y nginx

# Start nginx
sudo systemctl start nginx

# Enable nginx to start on boot
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

## Configuration

### Documentation Server

For serving MkDocs documentation:

1. **Copy configuration:**
   ```bash
   sudo cp scripts/nginx/nginx_docs.conf /etc/nginx/sites-available/docs
   ```

2. **Enable site:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/docs /etc/nginx/sites-enabled/
   ```

3. **Test configuration:**
   ```bash
   sudo nginx -t
   ```

4. **Reload nginx:**
   ```bash
   sudo systemctl reload nginx
   ```

### Main Application

For serving the full Bifrost application:

1. **Copy configuration:**
   ```bash
   sudo cp scripts/nginx/bifrost.conf /etc/nginx/sites-available/bifrost
   ```

2. **Enable site:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/bifrost /etc/nginx/sites-enabled/
   ```

3. **Remove default site (optional):**
   ```bash
   sudo rm /etc/nginx/sites-enabled/default
   ```

4. **Test and reload:**
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

## Removing Existing Nginx

If nginx is already installed and you want a fresh installation:

```bash
# Stop nginx
sudo systemctl stop nginx

# Remove nginx completely
sudo apt-get remove --purge nginx nginx-common nginx-core

# Clean up
sudo apt-get autoremove -y
sudo apt-get autoclean

# Remove configuration
sudo rm -rf /etc/nginx
sudo rm -rf /var/log/nginx

# Kill any remaining processes
sudo pkill -9 nginx

# Reinstall
sudo apt-get update
sudo apt-get install -y nginx
```

## Verification

### Test HTTP Access

```bash
# From server
curl http://localhost/docs/

# From another PC
curl http://10.0.0.75/docs/
```

### Check Service Status

```bash
sudo systemctl status nginx
```

### Check Configuration

```bash
sudo nginx -t
```

### Check Listening Ports

```bash
sudo netstat -tlnp | grep nginx
# or
sudo ss -tlnp | grep nginx
```

## Firewall Configuration

If using UFW:

```bash
# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS (if configured)
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

## SSL/HTTPS Setup (Optional)

### Using Let's Encrypt

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (already configured)
sudo certbot renew --dry-run
```

### Manual SSL Configuration

1. Obtain SSL certificates
2. Update nginx configuration with SSL settings
3. Configure firewall for port 443
4. Test and reload nginx

See configuration files for SSL examples.

## Maintenance

### Regular Tasks

- **Monitor logs**: Check error and access logs regularly
- **Update nginx**: `sudo apt-get update && sudo apt-get upgrade nginx`
- **Backup configs**: Backup `/etc/nginx/` before major changes
- **Test changes**: Always run `nginx -t` before reloading

### Backup Configuration

```bash
# Backup nginx configuration
sudo tar -czf nginx-backup-$(date +%Y%m%d).tar.gz /etc/nginx/
```

### Restore Configuration

```bash
# Extract backup
sudo tar -xzf nginx-backup-YYYYMMDD.tar.gz -C /
sudo nginx -t
sudo systemctl reload nginx
```

## Troubleshooting

See [CONFIGURATION.md](CONFIGURATION.md) for detailed troubleshooting.

## Related Documentation

- [Nginx README](README.md) - Overview and quick reference
- [Configuration Guide](CONFIGURATION.md) - Detailed configuration
- [Documentation Deployment](../DEPLOYMENT.md) - Deploying docs

