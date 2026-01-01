# Documentation Deployment Guide

This guide explains how to deploy the MkDocs documentation to the web server (10.0.0.75) for access from any PC on the network.

## Overview

The documentation is built locally and deployed to the web server where it's served via nginx. This allows any PC on the network to access the documentation at `http://10.0.0.75/docs/`.

## Prerequisites

### On Dev PC (10.0.0.90)
- MkDocs installed: `pip install mkdocs mkdocs-material`
- SSH access to web server (10.0.0.75)
- SSH key configured for passwordless access

### On Web Server (10.0.0.75)
- Nginx installed
- User has sudo permissions
- Port 80 open in firewall

## Quick Start

### 1. Initial Setup (One-time, on Web Server)

SSH into the web server and run:

```bash
ssh vision@10.0.0.75
sudo ./scripts/docs/setup_web_server.sh
```

Or manually:

```bash
# Copy setup script to server
scp scripts/docs/setup_web_server.sh vision@10.0.0.75:~/

# SSH and run
ssh vision@10.0.0.75
sudo bash ~/setup_web_server.sh
```

### 2. Deploy Documentation (From Dev PC)

From your dev PC (10.0.0.90):

```bash
# Build and deploy
./scripts/docs/deploy_docs.sh
```

This will:
1. Build the MkDocs site locally
2. Copy files to web server
3. Set proper permissions
4. Make docs available at `http://10.0.0.75/docs/`

## Manual Deployment

### Step 1: Build Documentation

```bash
./scripts/docs/build_docs.sh
```

This creates a `site/` directory with static HTML files.

### Step 2: Deploy to Web Server

```bash
# Copy files to web server
rsync -avz --delete site/ vision@10.0.0.75:/var/www/docs/

# Set permissions (on web server)
ssh vision@10.0.0.75 "sudo chown -R www-data:www-data /var/www/docs && sudo chmod -R 755 /var/www/docs"
```

## Nginx Configuration

The nginx configuration is located at:
- Template: `scripts/docs/nginx_docs.conf`
- Server: `/etc/nginx/sites-available/docs`

### Configuration Details

- **Port**: 80 (HTTP)
- **Document Root**: `/var/www/docs/`
- **URL Path**: `/docs/`
- **Gzip Compression**: Enabled
- **Static Asset Caching**: 30 days

### Access URLs

- **Local network**: `http://10.0.0.75/docs/`
- **Root redirect**: `http://10.0.0.75/` → redirects to `/docs/`
- **Health check**: `http://10.0.0.75/health`

## Updating Documentation

After making changes to documentation:

```bash
# Rebuild and redeploy
./scripts/docs/deploy_docs.sh
```

The script automatically:
- Builds the latest documentation
- Backs up existing version
- Deploys new version
- Preserves nginx configuration

## Troubleshooting

### Cannot Connect to Web Server

```bash
# Test SSH connection
ssh vision@10.0.0.75

# Test network connectivity
ping 10.0.0.75

# Check SSH key
ssh-copy-id vision@10.0.0.75  # If needed
```

### Nginx Not Serving Documentation

```bash
# On web server, check nginx status
sudo systemctl status nginx

# Check nginx configuration
sudo nginx -t

# Check nginx logs
sudo tail -f /var/log/nginx/error.log

# Reload nginx
sudo systemctl reload nginx
```

### Permission Issues

```bash
# On web server, fix permissions
sudo chown -R www-data:www-data /var/www/docs
sudo chmod -R 755 /var/www/docs
```

### Documentation Not Updating

```bash
# Clear browser cache
# Or use incognito/private mode

# Check if files were deployed
ssh vision@10.0.0.75 "ls -la /var/www/docs/"

# Force rebuild
rm -rf site/
./scripts/docs/build_docs.sh
./scripts/docs/deploy_docs.sh
```

## Access from Other PCs

Once deployed, any PC on the network can access:

```
http://10.0.0.75/docs/
```

### Requirements
- PC must be on the same network (10.0.0.x)
- Firewall on web server must allow port 80
- No authentication required (public documentation)

## HTTPS Setup (Optional)

For secure access, configure HTTPS:

1. Obtain SSL certificate (Let's Encrypt, self-signed, etc.)
2. Update nginx configuration with SSL settings
3. Configure firewall for port 443
4. Access via `https://10.0.0.75/docs/`

See `scripts/docs/nginx_docs.conf` for HTTPS example configuration.

## Automated Deployment

### Using CI/CD (Future)

You can set up automated deployment:

```yaml
# .github/workflows/deploy-docs.yml
name: Deploy Documentation
on:
  push:
    branches: [main]
    paths: ['docs/**', 'mkdocs.yml']
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: pip install mkdocs mkdocs-material
      - run: mkdocs build
      - run: ./scripts/docs/deploy_docs.sh
```

## File Structure

```
scripts/docs/
├── build_docs.sh          # Build documentation locally
├── deploy_docs.sh          # Deploy to web server
├── setup_web_server.sh     # Initial nginx setup (run on server)
└── nginx_docs.conf        # Nginx configuration template

site/                       # Built documentation (generated)
└── index.html             # Documentation homepage
```

## Maintenance

### Regular Updates

Update documentation whenever:
- New features are added
- API changes occur
- Database schema changes
- Project structure changes

### Backup

The deployment script automatically backs up previous versions:
- Location: `/var/www/docs.backup.YYYYMMDD_HHMMSS/`
- Manual backup: `ssh vision@10.0.0.75 "sudo cp -r /var/www/docs /var/www/docs.backup.manual"`

## Summary

1. **Initial Setup** (one-time): Run `setup_web_server.sh` on web server
2. **Deploy**: Run `deploy_docs.sh` from dev PC
3. **Access**: Open `http://10.0.0.75/docs/` from any PC
4. **Update**: Run `deploy_docs.sh` after documentation changes

---

**Last Updated**: 2026-01-01

