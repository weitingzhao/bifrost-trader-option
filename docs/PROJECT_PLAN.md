# Bifrost Options Trading Strategy Analyzer - Comprehensive Project Plan

## Executive Summary

Bifrost is a professional options trading strategy analyzer system that integrates with Interactive Brokers to provide real-time option chain data, strategy analysis, historical tracking, and ML-based optimization. The system uses a hybrid architecture combining FastAPI for high-performance trading APIs and Django for data management, deployed across multiple machines for optimal performance and separation of concerns.

## Architecture Overview

### Technology Stack Decision

**Backend Framework**: Hybrid FastAPI + Django
- **FastAPI (Port 8000)**: High-performance trading API, real-time data, async operations with IB Gateway
- **Django (Port 8001)**: Admin interface, data management, complex queries, migrations
- **Shared Database**: PostgreSQL + TimescaleDB (both frameworks access same database)

**Rationale**: FastAPI excels at real-time trading operations and async IB integration, while Django provides excellent admin interface and data management capabilities. Both share the same database for consistency.

**UI Tools**:
- **React/Vue Frontend**: Production trading interface (Web-Server)
- **Streamlit**: System monitoring and analytics dashboards (Dev PC)
- **Django Admin**: Data management and CRUD operations (APP-SERVER)

### Multi-Machine Deployment Architecture

```mermaid
flowchart TD
    User[User Browser] --> WebServer[Web-Server<br/>10.0.0.75<br/>Nginx + React/Vue]
    WebServer -->|API Requests| APIServer[APP-SERVER<br/>10.0.0.80<br/>FastAPI:8000 + Django:8001]
    APIServer --> IBGateway[IB Gateway<br/>Headless<br/>10.0.0.80:7497]
    APIServer --> Database[(PostgreSQL<br/>TimescaleDB<br/>10.0.0.80:5432)]
    APIServer --> MLServer[RTX4090-Server<br/>10.0.0.60:8001<br/>ML Services]
    IBGateway --> IB[Interactive Brokers]
    DevPC[Dev PC<br/>10.0.0.90<br/>Streamlit Monitoring] -.Monitor.-> APIServer
    DataCollector[Data Collector<br/>APP-SERVER] --> IBGateway
    DataCollector --> Database
```

### Machine Roles

1. **Dev PC (10.0.0.90 - Mac)**
   - Development environment
   - SSH management hub for all servers
   - Streamlit monitoring dashboard (port 8501)
   - Deployment scripts and service management

2. **APP-SERVER (10.0.0.80 - Linux)**
   - FastAPI trading API (port 8000)
   - Django admin interface (port 8001)
   - PostgreSQL + TimescaleDB (port 5432)
   - IB Gateway headless mode (port 7497/7496)
   - Data collection services
   - Background job processing (Celery)

3. **Web-Server (10.0.0.75 - Linux)**
   - Nginx reverse proxy (ports 80/443)
   - React/Vue frontend static files
   - API proxy to APP-SERVER
   - WebSocket proxy for real-time updates

4. **RTX4090-Server (10.0.0.60 - Linux)**
   - ML/AI services (port 8001)
   - GPU-accelerated strategy optimization
   - Model training and prediction
   - Backtesting services

## Project Structure

```
bifrost-trader-option/
├── src/                          # FastAPI Application (Trading API)
│   ├── api/
│   │   ├── main.py              # FastAPI app initialization
│   │   ├── routes/              # API route handlers
│   │   │   ├── health.py
│   │   │   ├── options.py       # Options chain endpoints
│   │   │   ├── strategies.py    # Strategy analysis endpoints
│   │   │   └── history.py      # Historical data endpoints
│   │   ├── middleware/          # Auth, logging
│   │   └── dependencies.py
│   ├── core/                    # Core business logic
│   │   ├── config.py
│   │   ├── ib_connector.py     # IB connection manager
│   │   ├── options_chain.py
│   │   └── cache.py
│   ├── strategies/              # Strategy implementations
│   ├── analyzer/                # Analysis engines
│   ├── database/                # SQLAlchemy models & repositories
│   └── utils/
│
├── app_admin/                   # Django Application (Admin & Management)
│   ├── manage.py
│   ├── django_config/            # Django settings
│   └── apps/
│       ├── options/             # Options data models & admin
│       ├── strategies/          # Strategy history models & admin
│       └── data_collection/     # Data collection management commands
│
├── frontend/                     # React/Vue Frontend (Production UI)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/           # API client (calls FastAPI)
│   │   └── utils/
│   └── package.json
│
├── app_monitor/              # Streamlit Applications
│   ├── monitoring/              # System monitoring (existing)
│   └── analytics/                # Strategy analytics dashboards
│       ├── app.py
│       └── pages/
│           ├── strategy_performance.py
│           ├── option_chain_viewer.py
│           └── profit_analysis.py
│
├── ml_services/                 # ML/AI Services (RTX4090-Server)
│   ├── api/                     # ML API endpoints
│   ├── models/                  # ML model definitions
│   ├── training/                # Training scripts
│   └── features/                # Feature engineering
│
├── services/                     # Background Services
│   ├── data_collector.py        # Periodic option collection
│   └── history_service.py      # Historical data management
│
├── shared/                       # Shared code
│   ├── database/                # Shared DB utilities
│   └── schemas/                 # Shared data schemas
│
├── scripts/
│   ├── management/              # Server management (existing)
│   ├── database/                # DB management scripts
│   └── deployment/              # Deployment scripts
│
├── tests/
├── docker/
└── docs/
    ├── api/                     # API documentation (keep)
    │   ├── API_DEVELOPMENT_GUIDE.md
    │   └── API_CHANGELOG.md
    └── PROJECT_PLAN.md          # This consolidated plan
```

## Database Architecture

### Shared Database: PostgreSQL + TimescaleDB

Both FastAPI (SQLAlchemy) and Django (Django ORM) access the same database:

**Key Tables**:
- `stocks`: Stock symbols and metadata
- `option_snapshots`: TimescaleDB hypertable for option chain history
- `strategy_history`: Historical strategy analysis results
- `market_conditions`: Market state snapshots

**Schema Management**: Django manages migrations (source of truth), SQLAlchemy models mirror Django models.

## Open Source Tools & Libraries

### Phase 1: Essential (Immediate)
- **Plotly** (>=5.0.0): Interactive charts for option chains, Greeks, P&L profiles
- **Celery** (>=5.3.0) + **Redis**: Distributed task queue for data collection
- **py_vollib** (>=1.0.1): Options pricing and Greeks (Black-Scholes)
- **APScheduler** (>=3.10.0): Simple scheduling for background jobs

### Phase 2: Short-term
- **VectorBT** (>=0.25.0): Fast vectorized backtesting for options
- **QuantLib-Python** (>=1.31): Advanced pricing models
- **TA-Lib** (>=0.4.0): Technical analysis indicators

### Phase 3: Medium-term
- **Backtrader** (>=1.9.0): Comprehensive backtesting framework
- **yfinance** (>=0.2.0): Free market data
- **TradingView Lightweight Charts**: Frontend charting library (npm)

## Implementation Phases

### Phase 1: Foundation (Current → 2 weeks)
**Status**: ✅ Complete
- [x] FastAPI basic structure
- [x] IB connector integration
- [x] Streamlit monitoring
- [x] Restructure `src/` to match recommended structure
- [x] Set up Django project structure
- [x] Configure shared database
- [x] Set up Celery for background jobs

### Phase 2: Data Infrastructure (Weeks 3-4)
**Status**: Code complete, deployment pending
- [ ] Install PostgreSQL + TimescaleDB on APP-SERVER
- [x] Create database schema (Django models)
- [x] Create SQLAlchemy models matching Django
- [x] Implement data collector service (Celery)
- [x] Set up scheduled option chain collection
- [x] Configure Django admin for all models

### Phase 3: Enhanced Features (Weeks 5-6)
**Status**: Code complete, database connection pending
- [x] Add Plotly charts to Streamlit analytics
- [x] Implement historical data API endpoints
- [x] Create Streamlit analytics dashboard
- [x] Integrate VectorBT for backtesting
- [x] Add py_vollib for advanced pricing
- [x] Implement option chain visualization

### Phase 4: Frontend & ML (Weeks 7-8)
- [ ] Build React/Vue frontend
- [ ] Deploy frontend to Web-Server
- [ ] Configure Nginx reverse proxy
- [ ] Set up ML services on RTX4090-Server
- [ ] Integrate ML API with FastAPI
- [ ] Add TradingView charts to frontend

### Phase 5: Production Deployment (Weeks 9-10)
- [ ] Set up systemd services for all components
- [ ] Configure Nginx on Web-Server
- [ ] Set up SSL certificates
- [ ] Implement monitoring and alerting
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Documentation completion

## Key Design Decisions

### 1. Hybrid FastAPI + Django
**Decision**: Use both frameworks for their strengths
- FastAPI: Trading API, real-time operations, async IB integration
- Django: Admin interface, data management, migrations
- Both share PostgreSQL database

### 2. Multi-Machine Deployment
**Decision**: Separate concerns across 4 machines
- APP-SERVER: All backend services (API, DB, IB Gateway)
- Web-Server: Frontend and reverse proxy
- RTX4090-Server: ML services only
- Dev PC: Development and monitoring

### 3. UI Tool Selection
**Decision**: Use appropriate tool for each use case
- React/Vue: Production trading interface
- Streamlit: Monitoring and analytics (internal)
- Django Admin: Data management (internal)

### 4. Database Co-location
**Decision**: Database on APP-SERVER with API
- Low latency between API and database
- Simpler networking
- Can scale later if needed

### 5. IB Gateway Architecture
**Decision**: Single IB Gateway instance with connection pooling
- One IB Gateway on APP-SERVER
- Multiple client IDs for different services
- Connection pool for load balancing

## Data Flow

### Real-time Trading Request
```
User → Web-Server (Nginx) → FastAPI (8000) → IB Gateway → IB
                                                      ↓
                                              Store via SQLAlchemy
                                                      ↓
                                              PostgreSQL (TimescaleDB)
```

### Data Collection
```
Celery Scheduled Task → IB Gateway → IB
                              ↓
                    Django ORM → PostgreSQL
```

### Strategy Analysis with ML
```
User Request → FastAPI → Query Current Options (IB)
                    ↓
            Query Historical Data (PostgreSQL)
                    ↓
            ML Service (RTX4090-Server)
                    ↓
            Return Combined Results
```

## Configuration

### Environment Variables

**APP-SERVER (.env)**:
```env
# IB Connection
IB_HOST=127.0.0.1
IB_PORT=7497
IB_CLIENT_ID=1

# Database (shared)
DATABASE_URL=postgresql://user:pass@localhost:5432/options_db

# FastAPI
APP_HOST=0.0.0.0
APP_PORT=8000

# Django
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=False

# ML Service
ML_API_URL=http://10.0.0.60:8001

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
```

## Security Considerations

- SSH key-based authentication between servers
- Database password protection
- API authentication (JWT tokens - future)
- Firewall rules to restrict access
- Network isolation (local network)
- SSL/TLS for production (Let's Encrypt)

## Monitoring & Maintenance

- **Streamlit Monitoring**: Real-time system health (Dev PC)
- **Django Admin**: Data management and monitoring
- **Health Checks**: Automated checks across all machines
- **Logging**: Centralized logging (optional: ELK stack)
- **Backups**: Automated database backups
- **Alerts**: Service failure notifications

## Scalability Path

1. **Horizontal Scaling**: Add more APP-SERVER instances behind load balancer
2. **Database Replication**: Master-slave PostgreSQL replication
3. **Caching Layer**: Redis for frequently accessed data
4. **Message Queue**: RabbitMQ/Kafka for async processing
5. **CDN**: For frontend static assets (if public)

## Next Steps

1. Review and approve this consolidated plan
2. Begin Phase 1: Restructure codebase to match recommended structure
3. Set up Django project alongside FastAPI
4. Configure shared database
5. Implement data collection service

## Documentation Structure

This plan consolidates all previous architectural design documents:
- Multi-machine deployment architecture
- Hybrid FastAPI + Django architecture
- Technology stack decisions
- UI tool selection rationale
- Open source tools and libraries
- Implementation phases and timelines

For API-specific documentation, see:
- `docs/api/API_DEVELOPMENT_GUIDE.md`: API development best practices
- `docs/api/API_CHANGELOG.md`: API version tracking

