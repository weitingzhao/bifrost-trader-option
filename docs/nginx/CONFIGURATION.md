# Nginx Configuration Reference

Detailed reference for nginx configuration files and settings.

## Configuration Files

### Documentation Server (`nginx_docs.conf`)

Serves MkDocs documentation at `/docs/`:

```nginx
server {
    listen 80;
    server_name 10.0.0.75;
    
    location /docs/ {
        alias /var/www/docs/;
        index index.html;
        try_files $uri $uri/ =404;
        
        # Compression
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css text/xml text/javascript 
                   application/x-javascript application/xml+rss application/json;
        
        # Cache static assets
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
```

### Main Application (`bifrost.conf`)

Serves frontend and proxies to backends:

```nginx
upstream fastapi_backend {
    server 10.0.0.80:8000;
}

upstream django_backend {
    server 10.0.0.80:8001;
}

server {
    listen 80;
    server_name bifrost.local;
    
    # Frontend static files
    location / {
        root /opt/bifrost-frontend/build;
        try_files $uri $uri/ /index.html;
    }
    
    # FastAPI API endpoints
    location /api/ {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Django admin
    location /admin/ {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket support
    location /ws/ {
        proxy_pass http://fastapi_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Configuration Directories

### `/etc/nginx/`
Main nginx configuration directory:
- `nginx.conf` - Main configuration file
- `sites-available/` - Available site configurations
- `sites-enabled/` - Enabled site configurations (symlinks)
- `conf.d/` - Additional configuration files
- `modules-available/` - Available modules
- `modules-enabled/` - Enabled modules

### `/var/log/nginx/`
Log files:
- `access.log` - Access logs
- `error.log` - Error logs

## Key Settings

### Worker Processes
```nginx
worker_processes auto;  # Auto-detect CPU cores
```

### Connection Handling
```nginx
events {
    worker_connections 1024;
    use epoll;  # Efficient event model
}
```

### Gzip Compression
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

### Timeouts
```nginx
proxy_connect_timeout 60s;
proxy_send_timeout 60s;
proxy_read_timeout 60s;
```

### Buffer Sizes
```nginx
client_body_buffer_size 128k;
client_max_body_size 10m;
proxy_buffer_size 4k;
proxy_buffers 4 32k;
proxy_busy_buffers_size 64k;
```

## Proxy Settings

### Basic Proxy
```nginx
location /api/ {
    proxy_pass http://backend;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

### WebSocket Proxy
```nginx
location /ws/ {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### Load Balancing
```nginx
upstream backend {
    server 10.0.0.80:8000;
    server 10.0.0.81:8000 backup;
}
```

## SSL/HTTPS Configuration

### Basic SSL
```nginx
server {
    listen 443 ssl http2;
    server_name example.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
}
```

### HTTP to HTTPS Redirect
```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}
```

## Caching

### Static File Caching
```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### Proxy Caching
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=10g;

location /api/ {
    proxy_cache my_cache;
    proxy_cache_valid 200 10m;
    proxy_pass http://backend;
}
```

## Security Headers

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## Troubleshooting

### Configuration Test
```bash
sudo nginx -t
```

### Check Syntax
```bash
sudo nginx -T  # Show full configuration
```

### Debug Mode
```nginx
error_log /var/log/nginx/error.log debug;
```

### Common Errors

1. **502 Bad Gateway**
   - Backend service not running
   - Firewall blocking connection
   - Wrong proxy_pass URL

2. **403 Forbidden**
   - File permissions incorrect
   - SELinux blocking access
   - Directory index disabled

3. **404 Not Found**
   - Document root incorrect
   - try_files directive missing
   - File doesn't exist

4. **Connection Refused**
   - Backend not listening on port
   - Wrong IP/port in upstream

## Performance Tuning

### Worker Processes
```nginx
worker_processes auto;  # Match CPU cores
```

### Keepalive Connections
```nginx
keepalive_timeout 65;
keepalive_requests 100;
```

### File Descriptors
```bash
# Increase system limit
ulimit -n 65536
```

## Monitoring

### Access Logs
```bash
# Real-time monitoring
sudo tail -f /var/log/nginx/access.log

# Count requests
sudo awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn
```

### Error Logs
```bash
# Real-time errors
sudo tail -f /var/log/nginx/error.log

# Recent errors
sudo grep error /var/log/nginx/error.log | tail -20
```

## Related Documentation

- [Nginx README](README.md) - Overview
- [Setup Guide](SETUP.md) - Installation and setup
- [Deploy Documentation Script](../../scripts/docs/deploy_docs.sh) - Script to deploy MkDocs to web server

