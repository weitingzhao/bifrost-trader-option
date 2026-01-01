# Testing Documentation

This directory contains all testing-related documentation for the Bifrost project.

## Files

### Test Strategy & Coverage
- **[TEST_STRATEGY.md](TEST_STRATEGY.md)** - Comprehensive test strategies for Phases 1-3
- **[TEST_DATABASE_COVERAGE.md](TEST_DATABASE_COVERAGE.md)** - Database test coverage explanation
- **[TEST_AND_SCHEMA_SUMMARY.md](TEST_AND_SCHEMA_SUMMARY.md)** - Quick reference for tests and schema

### Test Fixes & Warnings
- **[TEST_FIXES.md](TEST_FIXES.md)** - Details of fixes applied to resolve test errors
- **[TEST_WARNINGS_FIXED.md](TEST_WARNINGS_FIXED.md)** - Details of fixes for test warnings

## Quick Links

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/test_phase1_foundation.py
pytest tests/test_phase2_data_infrastructure.py
pytest tests/test_phase3_enhanced_features.py
pytest tests/test_database_operations.py
```

### Test Strategy
- See [TEST_STRATEGY.md](TEST_STRATEGY.md) for detailed test cases
- Review [TEST_DATABASE_COVERAGE.md](TEST_DATABASE_COVERAGE.md) for database testing

### Troubleshooting
- **Test failures**: Check [TEST_FIXES.md](TEST_FIXES.md)
- **Warnings**: See [TEST_WARNINGS_FIXED.md](TEST_WARNINGS_FIXED.md)
- **Database tests**: Review [TEST_DATABASE_COVERAGE.md](TEST_DATABASE_COVERAGE.md)

## Test Structure

```
tests/
├── test_phase1_foundation.py          # Phase 1 tests
├── test_phase2_data_infrastructure.py # Phase 2 tests
├── test_phase3_enhanced_features.py   # Phase 3 tests
├── test_database_operations.py        # Database CRUD tests
├── test_database_integration.py       # Database integration tests
└── conftest.py                        # Pytest configuration
```

## Related Documentation

- Main project plan: [../PROJECT_PLAN.md](../PROJECT_PLAN.md)
- Database setup: [../database/](../database/)
- Development guides: [../development/](../development/)

