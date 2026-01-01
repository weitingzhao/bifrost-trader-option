# Test Suite Documentation

## Overview

The test suite is organized into several categories:

1. **Phase Tests** - Verify implementation completion for each phase
2. **Database Operations Tests** - Test actual database CRUD operations
3. **Database Integration Tests** - Test with real database connections
4. **Strategy Tests** - Test strategy calculations

## Test Categories

### Phase Tests

- `test_phase1_foundation.py` - Tests for Phase 1 tasks
- `test_phase2_data_infrastructure.py` - Tests for Phase 2 tasks
- `test_phase3_enhanced_features.py` - Tests for Phase 3 tasks

These tests verify that:
- Code structure exists
- Modules can be imported
- Required classes/functions exist
- Configuration is correct

### Database Operations Tests

- `test_database_operations.py` - **NEW** - Tests actual database operations

These tests verify:
- ✅ Database connection works
- ✅ Tables can be created
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Repository methods work correctly
- ✅ Transactions (commit/rollback) work
- ✅ Query filtering works

**Uses**: In-memory SQLite database for fast, isolated testing

### Database Integration Tests

- `test_database_integration.py` - **NEW** - Tests with real database

These tests verify:
- Real database connection
- Table creation in actual database
- Performance with bulk operations
- Integration with actual database URL

**Requires**: DATABASE_URL environment variable or test database

### Strategy Tests

- `test_strategies.py` - Tests strategy calculations

## Running Tests

### Run All Tests

```bash
./tests/run_all_tests.sh
```

### Run Specific Test Categories

```bash
# Phase tests only
pytest tests/test_phase1_foundation.py -v
pytest tests/test_phase2_data_infrastructure.py -v
pytest tests/test_phase3_enhanced_features.py -v

# Database operations tests (in-memory SQLite)
pytest tests/test_database_operations.py -v

# Database integration tests (requires real DB)
pytest tests/test_database_integration.py -v

# Strategy tests
pytest tests/test_strategies.py -v
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html tests/
```

## Test Database Setup

### For Database Operations Tests

Uses in-memory SQLite - no setup required! Tests are isolated and fast.

### For Database Integration Tests

Requires actual database:

1. **Option 1: Use test database**
   ```bash
   export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/test_db"
   pytest tests/test_database_integration.py -v
   ```

2. **Option 2: Use SQLite file**
   ```bash
   export DATABASE_URL="sqlite+aiosqlite:///./test.db"
   pytest tests/test_database_integration.py -v
   ```

## What's Tested

### ✅ Currently Tested

- Model structure and imports
- Database connection configuration
- CRUD operations (Create, Read, Update, Delete)
- Repository methods
- Transaction handling
- Query filtering

### ⚠️ Not Yet Tested (Future)

- Django ORM operations
- TimescaleDB-specific features
- Database migrations
- Concurrent access
- Performance under load
- Data integrity constraints

## Test Dependencies

Add to `requirements.txt`:
- `pytest>=7.4.0`
- `pytest-asyncio>=0.21.0`
- `aiosqlite>=0.19.0` (for in-memory SQLite tests)

## Notes

- Database operations tests use in-memory SQLite for speed and isolation
- Integration tests require actual database connection
- Some tests may skip if dependencies are not installed (expected)
- Tests are designed to be run in CI/CD pipelines

