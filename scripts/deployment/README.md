# Deployment Scripts

Deployment scripts and configurations for Bifrost services.

## Status

⚠️ **Placeholder**: These are placeholder deployment configurations. Full deployment automation will be implemented in Phase 5.

## Structure

```
scripts/deployment/
├── deploy.sh              # Main deployment script
├── systemd/               # Systemd service files
│   ├── fastapi.service
│   ├── django.service
│   └── celery.service
├── nginx/                 # Nginx configurations
│   └── bifrost.conf
└── README.md             # This file
```

## Systemd Services

Service files for managing Bifrost components:

- **fastapi.service**: FastAPI trading API (port 8000)
- **django.service**: Django admin interface (port 8001)
- **celery.service**: Celery worker for background jobs

## Nginx Configuration

Reverse proxy configuration for Web-Server (10.0.0.75):

- Frontend static files serving
- API proxy to FastAPI (10.0.0.80:8000)
- Admin proxy to Django (10.0.0.80:8001)
- WebSocket support for real-time updates

## Phase 5 Implementation

Full deployment automation will include:

1. **Server Setup**
   - SSH key-based authentication
   - Dependency installation
   - User and directory creation

2. **Service Deployment**
   - Copy application files
   - Set up virtual environments
   - Install Python dependencies
   - Configure systemd services
   - Start services

3. **Database Setup**
   - PostgreSQL + TimescaleDB installation
   - Database creation
   - Schema migration (Django)
   - Initial data setup

4. **Nginx Configuration**
   - Install and configure Nginx
   - Set up reverse proxy
   - SSL certificate setup (Let's Encrypt)
   - Frontend deployment

5. **Monitoring & Health Checks**
   - Service health verification
   - Log aggregation setup
   - Alerting configuration

## Usage

```bash
# Deploy to APP-SERVER
./deploy.sh app-server

# Deploy to Web-Server
./deploy.sh web-server

# Deploy all services
./deploy.sh all
```

## Manual Deployment Steps (Current)

Until Phase 5 automation is complete, services can be deployed manually:

1. Copy files to target server
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`
4. Copy systemd service files to `/etc/systemd/system/`
5. Enable and start services: `sudo systemctl enable --now <service>`
6. Configure Nginx and restart: `sudo systemctl restart nginx`

