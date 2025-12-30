# Documentation

This directory contains documentation for the Bifrost Options Trading Strategy Analyzer project.

## Documentation Files

- **[DEPLOYMENT_ARCHITECTURE.md](./DEPLOYMENT_ARCHITECTURE.md)**: Complete multi-machine deployment architecture plan
  - Machine roles and responsibilities
  - Network architecture and port assignments
  - Data flow diagrams
  - Configuration examples
  - SSH management setup
  - Implementation phases

## Quick Reference

### Machine Overview

- **Dev PC (10.0.0.90)**: Development and SSH management hub
- **APP-SERVER (10.0.0.80)**: FastAPI, PostgreSQL, IB Gateway (all services)
- **Web-Server (10.0.0.75)**: Nginx reverse proxy and frontend
- **RTX4090-Server (10.0.0.60)**: ML/AI services with GPU

### Key Services

- **IB Gateway**: Runs on APP-SERVER (10.0.0.80) in headless mode
- **FastAPI**: Main API server on APP-SERVER (10.0.0.80:8000)
- **PostgreSQL**: Database on APP-SERVER (10.0.0.80:5432)
- **ML API**: ML services on RTX4090-Server (10.0.0.60:8001)

## Related Documentation

- Main project README: [../README.md](../README.md)
- API documentation: Available at `/docs` endpoint when FastAPI is running

