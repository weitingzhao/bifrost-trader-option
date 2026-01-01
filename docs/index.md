# Bifrost Options Trading Strategy Analyzer

Welcome to the Bifrost documentation!

Bifrost is a professional options trading strategy analyzer system that integrates with Interactive Brokers to provide:
- Real-time option chain data from IB Gateway
- Strategy analysis (Covered Call, Iron Condor, etc.)
- Historical option tracking with PostgreSQL + TimescaleDB
- ML-based strategy optimization
- Multi-machine distributed deployment

## Quick Start

1. **Read the [Project Plan](PROJECT_PLAN.md)** for architecture overview
2. **Follow [Setup Guide](setup/NEXT_STEPS.md)** for installation
3. **Check [Database Documentation](database/index.md)** for database setup
4. **Review [API Development Guide](api/API_DEVELOPMENT_GUIDE.md)** for API development

## Documentation Structure

### 📋 Project Overview
- **[Project Plan](PROJECT_PLAN.md)** - Comprehensive project plan and architecture

### 🔌 API Documentation
- **[API Development Guide](api/API_DEVELOPMENT_GUIDE.md)** - API development best practices
- **[API Changelog](api/API_CHANGELOG.md)** - API version tracking

### 🗄️ Database
- **[Database Documentation](database/index.md)** ⭐ - Database schema management and guides (SINGLE SOURCE OF TRUTH)

### 🧪 Testing
- **[Test Strategy](testing/TEST_STRATEGY.md)** - Comprehensive test strategies
- **[Database Test Coverage](testing/TEST_DATABASE_COVERAGE.md)** - Database testing guide

### ⚙️ Setup & Installation
- **[Next Steps](setup/NEXT_STEPS.md)** - Step-by-step setup guide
- **[Setup Complete](setup/SETUP_COMPLETE.md)** - Setup verification

### 💻 Development
- **[Phase 1 Restructure](development/PHASE1_RESTRUCTURE.md)** - Project restructuring
- **[Structure Verification](development/STRUCTURE_VERIFICATION.md)** - Structure checklist

### 📊 Status & Progress
- **[Implementation Status](status/IMPLEMENTATION_STATUS.md)** - Current project status
- **[Phase 1 Complete](status/PHASE1_COMPLETE.md)** - Phase 1 completion summary

## Key Concepts

### Database Schema Management

**⭐ Single Source of Truth:** `scripts/database/schema.sql`

All database changes must follow this workflow:
1. Update `scripts/database/schema.sql` (SINGLE SOURCE OF TRUTH)
2. Update Django models
3. Generate Django migrations
4. Update SQLAlchemy models
5. Verify all are in sync

See [Database Documentation](database/index.md) for details.

### Architecture

- **FastAPI** (Port 8000) - High-performance trading API
- **Django** (Port 8001) - Admin interface and data management
- **PostgreSQL + TimescaleDB** - Shared database
- **Multi-machine deployment** - Dev PC, APP-SERVER, Web-Server, RTX4090-Server

## Getting Help

- Check the [Project Plan](PROJECT_PLAN.md) for architecture decisions
- Review [API Development Guide](api/API_DEVELOPMENT_GUIDE.md) for API questions
- See [Database Documentation](database/index.md) for database changes
- Check [Test Strategy](testing/TEST_STRATEGY.md) for testing guidance

## Contributing

When making changes:
1. Follow the project structure rules
2. Update database schema via canonical workflow
3. Add tests for new functionality
4. Update relevant documentation
5. Verify all imports work correctly

---

**Last Updated:** 2026-01-01

