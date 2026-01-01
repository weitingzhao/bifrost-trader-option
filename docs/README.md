# Bifrost Documentation

This directory contains all project documentation organized by category.

## Documentation Structure

### Main Documentation
- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Comprehensive project plan and architecture
- **[index.md](index.md)** - Documentation homepage (for MkDocs)

### API Documentation
- **[api/API_DEVELOPMENT_GUIDE.md](api/API_DEVELOPMENT_GUIDE.md)** - API development best practices
- **[api/API_CHANGELOG.md](api/API_CHANGELOG.md)** - API version tracking

### Database Documentation
- **[database/README.md](database/README.md)** ⭐ - Database schema management and guides (SINGLE SOURCE OF TRUTH)
- **[database/DATABASE_CONNECTION_DBEAVER.md](database/DATABASE_CONNECTION_DBEAVER.md)** - Complete guide for connecting to PostgreSQL using DBeaver
- **[database/DATABASE_VERIFICATION.md](database/DATABASE_VERIFICATION.md)** - Guide for verifying database tables and schema
- **[database/REINSTALL_POSTGRESQL.md](database/REINSTALL_POSTGRESQL.md)** - Guide for completely removing and reinstalling PostgreSQL

### Testing Documentation
- **[testing/TEST_STRATEGY.md](testing/TEST_STRATEGY.md)** - Comprehensive test strategies for Phases 1-3
- **[testing/TEST_DATABASE_COVERAGE.md](testing/TEST_DATABASE_COVERAGE.md)** - Database test coverage explanation

### Setup & Installation
- **[setup/NEXT_STEPS.md](setup/NEXT_STEPS.md)** - Step-by-step implementation guide
- **[setup/SETUP_COMPLETE.md](setup/SETUP_COMPLETE.md)** - Setup scripts documentation

### Development Guides
- **[development/PHASE1_RESTRUCTURE.md](development/PHASE1_RESTRUCTURE.md)** - Phase 1 restructuring summary
- **[development/STRUCTURE_VERIFICATION.md](development/STRUCTURE_VERIFICATION.md)** - Project structure verification

### Status & Progress
- **[status/IMPLEMENTATION_COMPLETE.md](status/IMPLEMENTATION_COMPLETE.md)** - Implementation completion summary
- **[status/PHASE1_STATUS.md](status/PHASE1_STATUS.md)** - Phase 1 completion status

## Viewing Documentation

### Using MkDocs (Recommended)

```bash
# Install MkDocs
pip install mkdocs mkdocs-material mkdocs-git-revision-date-localized-plugin

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

Then open http://127.0.0.1:8000 in your browser.

### Direct Access

You can also read the markdown files directly in your editor or on GitHub.

## Quick Links

### Getting Started
1. Read [PROJECT_PLAN.md](PROJECT_PLAN.md) for architecture overview
2. Follow [setup/NEXT_STEPS.md](setup/NEXT_STEPS.md) for implementation
3. Check [database/README.md](database/README.md) for database setup

### Database Schema Changes
- ⭐ **Single Source of Truth:** `scripts/database/schema.sql`
- See [database/README.md](database/README.md) for workflow

### Development
- See [api/API_DEVELOPMENT_GUIDE.md](api/API_DEVELOPMENT_GUIDE.md) for API development
- Review [development/PHASE1_RESTRUCTURE.md](development/PHASE1_RESTRUCTURE.md) for project structure

