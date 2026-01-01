# Test Suite Documentation

## Overview

The test suite is organized into subdirectories by category for better organization and maintainability:

1. **Database Tests** (`tests/database/`) - Database operations and integration tests
2. **Strategy Tests** (`tests/strategies/`) - Strategy calculation tests
3. **Phase Tests** (`tests/phases/`) - Phase implementation verification tests

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared pytest configuration and fixtures
├── README.md                # This file
├── run_all_tests.sh         # Script to run all tests
│
├── database/                # Database-related tests
│   ├── __init__.py
│   ├── test_database_integration.py    # Integration tests with real database
│   └── test_database_operations.py     # CRUD operations tests (in-memory SQLite)
│
├── strategies/              # Strategy-related tests
│   ├── __init__.py
│   └── test_strategies.py              # Strategy calculation tests
│
└── phases/                  # Phase implementation tests
    ├── __init__.py
    ├── test_phase1_foundation.py       # Phase 1: Foundation tasks
    ├── test_phase2_data_infrastructure.py  # Phase 2: Data Infrastructure
    └── test_phase3_enhanced_features.py   # Phase 3: Enhanced Features
```

## Test Categories

### Database Tests (`tests/database/`)

#### `test_database_operations.py`
Tests actual database operations using in-memory SQLite:
- ✅ Database connection works
- ✅ Tables can be created
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Repository methods work correctly
- ✅ Transactions (commit/rollback) work
- ✅ Query filtering works

**Uses**: In-memory SQLite database for fast, isolated testing

#### `test_database_integration.py`
Integration tests that require real database connection:
- Real database connection
- Table creation in actual database
- Performance with bulk operations
- Integration with actual database URL

**Requires**: DATABASE_URL environment variable or test database

### Strategy Tests (`tests/strategies/`)

#### `test_strategies.py`
Tests strategy calculations:
- Covered Call strategy
- Iron Condor strategy
- Strategy profit/loss calculations
- Greeks calculations

### Phase Tests (`tests/phases/`)

#### `test_phase1_foundation.py`
Tests for Phase 1: Foundation tasks:
- FastAPI structure and routes
- Database configuration
- Project structure
- Module imports

#### `test_phase2_data_infrastructure.py`
Tests for Phase 2: Data Infrastructure:
- Django models
- SQLAlchemy models
- Repository patterns
- Data collection infrastructure

#### `test_phase3_enhanced_features.py`
Tests for Phase 3: Enhanced Features:
- Plotly charts in Streamlit
- VectorBT integration
- Enhanced analytics
- ML features

## Running Tests

### Run All Tests

```bash
./tests/run_all_tests.sh
```

Or using pytest directly:

```bash
pytest tests/ -v
```

### Run Specific Test Categories

```bash
# All database tests
pytest tests/database/ -v

# All strategy tests
pytest tests/strategies/ -v

# All phase tests
pytest tests/phases/ -v

# Specific test file
pytest tests/database/test_database_operations.py -v
pytest tests/database/test_database_integration.py -v
pytest tests/strategies/test_strategies.py -v
pytest tests/phases/test_phase1_foundation.py -v
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html tests/
```

### Run Specific Test Markers

```bash
# Run only integration tests
pytest -m integration tests/

# Skip slow tests
pytest -m "not slow" tests/
```

## Test Database Setup

### For Database Operations Tests

Uses in-memory SQLite - no setup required! Tests are isolated and fast.

```bash
pytest tests/database/test_database_operations.py -v
```

### For Database Integration Tests

Requires actual database:

1. **Option 1: Use test database**
   ```bash
   export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/test_db"
   pytest tests/database/test_database_integration.py -v
   ```

2. **Option 2: Use SQLite file**
   ```bash
   export DATABASE_URL="sqlite+aiosqlite:///./test.db"
   pytest tests/database/test_database_integration.py -v
   ```

## What's Tested

### ✅ Currently Tested

- Model structure and imports
- Database connection configuration
- CRUD operations (Create, Read, Update, Delete)
- Repository methods
- Transaction handling
- Query filtering
- Strategy calculations
- Phase implementation verification

### ⚠️ Not Yet Tested (Future)

- Django ORM operations
- TimescaleDB-specific features
- Database migrations
- Concurrent access
- Performance under load
- Data integrity constraints
- API endpoint testing
- End-to-end workflows

## Test Dependencies

Add to `requirements.txt`:
- `pytest>=7.4.0`
- `pytest-asyncio>=0.21.0`
- `aiosqlite>=0.19.0` (for in-memory SQLite tests)
- `pytest-cov>=4.1.0` (for coverage reports)

## Notes

- Database operations tests use in-memory SQLite for speed and isolation
- Integration tests require actual database connection
- Some tests may skip if dependencies are not installed (expected)
- Tests are designed to be run in CI/CD pipelines
- Test files are organized by category for better maintainability

## Adding New Tests

When adding new tests:

1. **Database tests** → Add to `tests/database/`
2. **Strategy tests** → Add to `tests/strategies/`
3. **Phase tests** → Add to `tests/phases/`
4. **New category** → Create new subdirectory with `__init__.py`

Make sure to:
- Update import paths (use `Path(__file__).parent.parent.parent` for project root)
- Add appropriate pytest markers (`@pytest.mark.integration`, etc.)
- Follow existing test patterns
- Update this README if adding new categories
