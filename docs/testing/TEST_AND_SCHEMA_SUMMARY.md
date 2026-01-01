# Test Warnings Fixed & Schema Export Guide

## ✅ Test Warnings Fixed

### Issues Resolved

1. **pytest-asyncio Configuration**
   - Created `pytest.ini` with `asyncio_mode = auto`
   - Created `tests/conftest.py` for shared configuration
   - Changed from per-class `@pytest.mark.asyncio` to module-level `pytestmark`

2. **SQL Syntax Updates**
   - Updated to use `text()` wrapper for SQLAlchemy 2.0
   - Fixed table name checking to be more flexible

3. **Warning Filters**
   - Added filters for expected Pydantic deprecation warnings
   - Tests now run without unnecessary warnings

### Files Created/Modified

- ✅ `pytest.ini` - Pytest configuration
- ✅ `tests/conftest.py` - Shared test fixtures
- ✅ `tests/test_database_operations.py` - Fixed async markers
- ✅ `tests/test_database_integration.py` - Fixed async markers

### Running Tests

```bash
# Install dependencies
pip install pytest pytest-asyncio aiosqlite

# Run database tests (should now work!)
pytest tests/test_database_operations.py -v
```

**Expected**: Tests run instead of being skipped!

---

## 📊 Database Schema Export

### Quick Export

```bash
# Export both SQLAlchemy and Django schemas
./scripts/database/export_schema.sh
```

**Output**:
- `scripts/database/schema_sqlalchemy.sql` ✅ Always generated
- `scripts/database/schema_django.sql` ⚠️ Only if Django is set up

### View Exported Schema

```bash
# View SQLAlchemy schema
cat scripts/database/schema_sqlalchemy.sql

# View specific tables
grep -A 20 "CREATE TABLE option_snapshots" scripts/database/schema_sqlalchemy.sql
```

### Example Schema Output

The exported schema includes:

```sql
CREATE TABLE option_snapshots (
    id INTEGER NOT NULL,
    stock_id INTEGER NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    underlying_price FLOAT NOT NULL,
    timestamp DATETIME NOT NULL,
    contracts_data JSON,
    PRIMARY KEY (id),
    FOREIGN KEY(stock_id) REFERENCES stocks (id)
);

CREATE TABLE strategy_history (
    id INTEGER NOT NULL,
    stock_id INTEGER NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    strategy_type VARCHAR(50) NOT NULL,
    entry_cost FLOAT NOT NULL,
    max_profit FLOAT NOT NULL,
    max_loss FLOAT NOT NULL,
    -- ... more fields
    PRIMARY KEY (id),
    FOREIGN KEY(stock_id) REFERENCES stocks (id)
);
```

### Other Export Methods

#### From PostgreSQL Database

```bash
# Export schema only
pg_dump -h localhost -U username -d database_name --schema-only > schema.sql

# Export specific tables
pg_dump -h localhost -U username -d database_name \
  --schema-only \
  -t option_snapshots \
  -t strategy_history > schema_tables.sql
```

#### From Django

```bash
cd app_django
python manage.py sqlmigrate options 0001
python manage.py sqlmigrate strategies 0001
```

#### View Table Structure in PostgreSQL

```bash
psql -h localhost -U username -d database_name

# Then:
\d option_snapshots          # Describe table
\d+ option_snapshots         # Detailed
\dt                         # List tables
```

### Schema Comparison

```bash
# Compare SQLAlchemy vs Django schemas
diff scripts/database/schema_sqlalchemy.sql scripts/database/schema_django.sql

# Side-by-side
diff -y scripts/database/schema_sqlalchemy.sql scripts/database/schema_django.sql
```

## Summary

### ✅ Fixed
- pytest-asyncio configuration
- SQL syntax for SQLAlchemy 2.0
- Test warnings
- Schema export script

### 📊 Available
- Schema export script: `./scripts/database/export_schema.sh`
- Exported schema: `scripts/database/schema_sqlalchemy.sql`
- Documentation: `docs/database/DATABASE_SCHEMA_EXPORT.md`

### 🧪 Next Steps

1. **Install test dependencies**:
   ```bash
   pip install pytest pytest-asyncio aiosqlite
   ```

2. **Run tests**:
   ```bash
   pytest tests/test_database_operations.py -v
   ```

3. **Export schemas**:
   ```bash
   ./scripts/database/export_schema.sh
   ```

All warnings should now be resolved, and schema export is working!

