# Multi-Machine Deployment Architecture

## Overview

Distributed deployment of the options trading strategy analyzer across 4 machines with separation of concerns, option history tracking, and ML-based strategy optimization.

## Machine Roles & Responsibilities

### 1. Dev PC (10.0.0.90 - Mac)

**Primary Role**: Development Environment + Central Management Hub

- **Development**: Code development and testing
- **SSH Management Hub**: Central control point for all remote servers
  - Remote deployment scripts
  - Service management (start/stop/restart)
  - Log viewing and monitoring
  - Health checks across all machines
  - Configuration management
  - Remote command execution

### 2. APP-SERVER (10.0.0.80 - Linux)

**Primary Role**: FastAPI Application Server + Database Server + IB Gateway

- **IB Gateway**: Run Interactive Brokers Gateway in headless mode (no GUI)
- **IB Connection**: Single point of connection to Interactive Brokers
- **FastAPI Backend**: Main API server hosting the strategy analyzer
- **Strategy Analysis**: Real-time strategy calculations (Covered Call, Iron Condor, etc.)
- **Request Handling**: Process API requests from web frontend
- **Option History Database**: PostgreSQL with TimescaleDB for option chain history
- **Data Storage**: Store historical option snapshots, changes, and strategy history
- **Data Collection**: Background service that periodically fetches option chains from IB

### 3. Web-Server (10.0.0.75 - Linux)

**Primary Role**: Web Frontend + Reverse Proxy

- **Web Frontend**: React/Vue.js frontend for user interface
- **Nginx/Reverse Proxy**: Route requests to APP-SERVER
- **Static Assets**: Serve frontend static files
- **WebSocket Proxy**: Proxy WebSocket connections for real-time updates

### 4. RTX4090-Server (10.0.0.60 - Linux)

**Primary Role**: ML/AI Services Only

- **ML/AI Services**: Strategy optimization using GPU
- **Model Training**: Train ML models on GPU for strategy recommendation
- **Prediction Service**: ML-based strategy suggestions API
- **Feature Engineering**: Extract features from historical option data (fetched from APP-SERVER database)
- **Backtesting**: Test strategies against historical data using GPU acceleration
- **Strategy Recommendation Engine**: ML-based strategy suggestions
- **Data Access**: Query historical data from APP-SERVER database via API or direct DB connection

## Architecture Diagram

```mermaid
flowchart TD
    User[User Browser] --> WebServer[Web-Server<br/>10.0.0.75<br/>Nginx + Frontend]
    WebServer --> APIServer[APP-SERVER<br/>10.0.0.80<br/>FastAPI + IB Gateway + DB]
    APIServer --> IBGateway[IB Gateway<br/>Headless<br/>10.0.0.80]
    APIServer --> Database[(PostgreSQL<br/>TimescaleDB<br/>10.0.0.80)]
    APIServer --> MLServer[RTX4090-Server<br/>10.0.0.60<br/>ML Services]
    MLServer --> MLService[ML Strategy Engine<br/>GPU Processing]
    IBGateway --> IB[Interactive Brokers]
    
    DataCollector[Data Collector Service<br/>10.0.0.80] --> IBGateway
    DataCollector --> Database
    MLServer --> Database
    
    APIServer --> Cache[Redis Cache<br/>Optional]
    
    DevPC[Dev PC<br/>10.0.0.90<br/>Management Hub] -.SSH Management.-> WebServer
    DevPC -.SSH Management.-> APIServer
    DevPC -.SSH Management.-> MLServer
```

## Network Architecture

### Port Assignments

- **Dev PC (10.0.0.90)**: 
  - SSH: 22
- **APP-SERVER (10.0.0.80)**:
  - IB Gateway: 7497 (paper) / 7496 (live)
  - FastAPI: 8000 (internal)
  - PostgreSQL: 5432 (internal)
  - SSH: 22
- **Web-Server (10.0.0.75)**:
  - Nginx: 80, 443
  - SSH: 22
- **RTX4090-Server (10.0.0.60)**:
  - ML API: 8001
  - SSH: 22

### Firewall Rules

- Web-Server (75) → APP-SERVER (80): Port 8000
- APP-SERVER (80) → RTX4090-Server (60): Port 8001 (ML API)
- RTX4090-Server (60) → APP-SERVER (80): Port 5432 (Database access)
- Data Collector (80) → APP-SERVER (80): Port 7497/7496 (Local IB Gateway)
- Data Collector (80) → APP-SERVER (80): Port 5432 (Local database)

## Data Flow

### 1. Real-time Option Chain Request

```
User → Web-Server (75) → APP-SERVER (80) → IB Gateway (80) → IB
                                                              ↓
Response ← Web-Server ← APP-SERVER ← IB Gateway ← IB
```

### 2. Option History Collection

```
Scheduled Job (APP-SERVER) → IB Gateway (80) → IB
                                              ↓
PostgreSQL (APP-SERVER) ← Process & Store ← IB Data
```

### 3. Strategy Analysis with History

```
User Request → Web-Server (75) → APP-SERVER (80)
                                    ↓
                            Query Current Options (APP-SERVER 80 - IB Gateway)
                                    ↓
                            Query Historical Data (APP-SERVER 80 - Database)
                                    ↓
                            ML Recommendations (RTX4090-Server 60)
                                    ↓
                            Return Analysis Results
```

## Component Breakdown

### 1. Option History Tracking System

**Location**: APP-SERVER (10.0.0.80)

**Components**:
- **Time-Series Database**: PostgreSQL with TimescaleDB extension for option chain history
- **Data Collection Service**: Background service that periodically fetches option chains
- **Change Detection**: Track option price changes, volume, open interest, Greeks
- **Historical Analysis**: Query historical option data for patterns

**Data Schema** (conceptual):
- `option_snapshots`: Timestamped option chain data
- `option_changes`: Delta tracking (price changes, volume changes)
- `strategy_history`: Historical strategy analysis results
- `market_conditions`: Market state at time of snapshot

### 2. Strategy Analysis Service

**Location**: APP-SERVER (10.0.0.80)

**Components**:
- **FastAPI Application**: Current strategy analyzer code
- **Real-time Analysis**: Analyze current option chains
- **Historical Comparison**: Compare current strategies with historical performance
- **Strategy Finder**: Find profitable opportunities using Iron Condor and other strategies

### 3. ML Strategy Optimization

**Location**: RTX4090-Server (10.0.0.60)

**Components**:
- **Feature Engineering**: Extract features from historical option data (fetched from APP-SERVER database)
- **Model Training**: Train models on GPU for strategy recommendation
- **Prediction Service**: API endpoint for ML-based strategy suggestions
- **Backtesting**: Test strategies against historical data using GPU acceleration
- **Data Access**: Query historical data from APP-SERVER database via API or direct DB connection

### 4. Web Frontend

**Location**: Web-Server (10.0.0.75)

**Components**:
- **Dashboard**: Real-time option chain visualization
- **Strategy Builder**: Interactive strategy configuration
- **History Viewer**: View option change history and trends
- **Strategy Results**: Display analysis results and rankings

## Configuration Files

### APP-SERVER (.env)

```env
IB_HOST=127.0.0.1
IB_PORT=7497
IB_CLIENT_ID=1
DATABASE_URL=postgresql://user:pass@localhost:5432/options_db
ML_API_URL=http://10.0.0.60:8001
APP_HOST=0.0.0.0
APP_PORT=8000
```

### APP-SERVER (Data Collector .env)

```env
IB_HOST=127.0.0.1
IB_PORT=7497
IB_CLIENT_ID=2
DATABASE_URL=postgresql://user:pass@localhost:5432/options_db
COLLECTION_INTERVAL=300  # 5 minutes
```

### RTX4090-Server (ML Service .env)

```env
DATABASE_URL=postgresql://user:pass@10.0.0.80:5432/options_db
ML_API_HOST=0.0.0.0
ML_API_PORT=8001
GPU_DEVICE=0
MODEL_PATH=/opt/bifrost-ml/models
```

## SSH Management & Remote Control

### Management Tools on Dev PC (10.0.0.90)

**Location**: `scripts/management/` directory on Dev PC

#### Server Configuration

- **`servers.conf`**: Configuration file with all server details
  ```ini
  [app-server]
  host=10.0.0.80
  user=your_user
  ssh_key=~/.ssh/id_rsa
  app_path=/opt/bifrost-trader
  ib_gateway_path=/opt/ibgateway
  db_path=/var/lib/postgresql
  
  [web-server]
  host=10.0.0.75
  user=your_user
  ssh_key=~/.ssh/id_rsa
  nginx_config=/etc/nginx/sites-available/bifrost
  
  [gpu-server]
  host=10.0.0.60
  user=your_user
  ssh_key=~/.ssh/id_rsa
  ml_api_path=/opt/bifrost-ml
  db_host=10.0.0.80
  db_port=5432
  ```

#### Key Management Scripts

- **`deploy.sh`**: Deploy code to all servers
- **`service-manager.sh`**: Unified service control (start/stop/restart/status)
- **`view-logs.sh`**: View logs from any server
- **`health-check.sh`**: Health check across all machines
- **`remote-exec.sh`**: Execute commands on remote servers
- **`db-backup.sh`**: Backup database from APP-SERVER
- **`db-status.sh`**: Check database status and connections

## Implementation Phases

### Phase 1: Infrastructure Setup

1. **Dev PC (10.0.0.90)**:
   - Set up SSH access and key-based authentication to all servers
   - Create SSH management scripts and tools
   - Set up SSH config for easy access
   - Create deployment and management scripts

2. **APP-SERVER (10.0.0.80)**:
   - Install Python 3.8+, dependencies
   - Install PostgreSQL + TimescaleDB
   - Install and configure IB Gateway (headless mode, no GUI)
   - Set up database schema for option history
   - Deploy FastAPI application
   - Configure IB Gateway connection (localhost:7497)
   - Configure firewall for IB Gateway port (7497/7496)
   - Set up systemd services for auto-start (FastAPI, IB Gateway, data collector)
   - Configure database access for RTX4090-Server (if needed)

3. **Web-Server (10.0.0.75)**:
   - Install Nginx
   - Configure reverse proxy to APP-SERVER
   - Set up SSL (optional, for local network)
   - Deploy frontend (if building one)

4. **RTX4090-Server (10.0.0.60)**:
   - Install Python ML stack (PyTorch/TensorFlow with GPU support)
   - Install CUDA and GPU drivers
   - Set up ML API service
   - Configure database access to APP-SERVER (10.0.0.80:5432) for historical data queries

### Phase 2: Option History System

1. **Data Collection Service**:
   - Background service on APP-SERVER
   - Periodically fetch option chains via local IB Gateway (localhost:7497)
   - Store snapshots in local TimescaleDB
   - Track changes and deltas

2. **History API Endpoints**:
   - Add endpoints to FastAPI for historical queries
   - Time-range queries for option chains
   - Change tracking endpoints
   - Historical strategy performance

### Phase 3: Enhanced Strategy Analysis

1. **Iron Condor Strategy Finder**:
   - Enhance existing Iron Condor analyzer
   - Use historical data to filter/rank opportunities
   - Compare current opportunities with historical patterns

2. **Strategy Recommendation**:
   - ML model training on historical data
   - Feature extraction from option chains
   - Prediction API on RTX4090-Server

### Phase 4: Frontend & Integration

1. **Web Dashboard**:
   - Option chain visualization
   - Strategy builder interface
   - History viewer with charts
   - Real-time updates via WebSocket

2. **Integration Testing**:
   - End-to-end testing across all machines
   - Performance optimization
   - Load testing

## Security Considerations

- SSH key-based authentication between servers
- Database password protection
- Firewall rules to restrict access
- API authentication (JWT tokens)
- Network isolation (local network only)

## Monitoring & Maintenance

- **Logging**: Centralized logging (optional: ELK stack)
- **Health Checks**: Monitor all services via SSH from Dev PC
- **Backup**: Database backups on APP-SERVER (automated via scripts)
- **Alerts**: Service failure notifications (can be integrated with scripts)
- **Remote Management**: All operations controlled from Dev PC via SSH

## Scalability Considerations

- **Load Balancing**: Multiple APP-SERVER instances (future)
- **Database Replication**: PostgreSQL replication (future)
- **Caching**: Redis for frequently accessed data (optional)

