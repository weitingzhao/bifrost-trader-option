# Database Schema Management Guide

## Single Source of Truth

**`scripts/database/schema_canonical.sql`** is the **single source of truth** for the database schema.

This file contains the complete, authoritative database schema definition that all other schema representations must match.

## Schema Change Process

### Workflow for Database Changes

When making any database schema changes, follow this process:

```
1. Update schema_canonical.sql (SINGLE SOURCE OF TRUTH)
   ↓
2. Update Django models (django_app/apps/*/models.py)
   ↓
3. Generate Django migrations (python manage.py makemigrations)
   ↓
4. Update SQLAlchemy models (src/database/models.py) to match
   ↓
5. Verify all three are in sync
```

### Step-by-Step Process

#### 1. Update Canonical Schema

Edit `scripts/database/schema_canonical.sql`:

```sql
-- Add your changes here
ALTER TABLE stocks ADD COLUMN market_cap BIGINT;
CREATE INDEX idx_stocks_market_cap ON stocks(market_cap);
```

**Important:**
- Document changes in the version tracking section at the bottom
- Use `IF NOT EXISTS` for idempotent operations
- Include comments for new tables/columns

#### 2. Update Django Models

Edit the appropriate Django model file:
- `django_app/apps/options/models.py` - For stocks, option_snapshots, option_contracts
- `django_app/apps/strategies/models.py` - For strategy_history, market_conditions
- `django_app/apps/data_collection/models.py` - For collection_jobs

```python
class Stock(models.Model):
    # ... existing fields ...
    market_cap = models.BigIntegerField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['market_cap'], name='idx_stocks_market_cap'),
        ]
```

#### 3. Generate Django Migrations

```bash
cd django_app
python manage.py makemigrations
python manage.py migrate
```

This creates migration files in `django_app/apps/*/migrations/`.

#### 4. Update SQLAlchemy Models

Edit `src/database/models.py` to match Django models:

```python
class Stock(Base):
    # ... existing fields ...
    market_cap = Column(BigInteger, nullable=True)
    
    __table_args__ = (
        Index('idx_stocks_market_cap', 'market_cap'),
    )
```

#### 5. Verify Synchronization

Run the verification script:

```bash
./scripts/database/verify_schema.py
```

Or manually compare:
- `scripts/database/schema_canonical.sql` (source of truth)
- Django models in `django_app/apps/*/models.py`
- SQLAlchemy models in `src/database/models.py`

## Schema Files

### Primary Files

1. **`scripts/database/schema_canonical.sql`** ⭐ **SINGLE SOURCE OF TRUTH**
   - Complete, authoritative schema definition
   - All changes start here
   - Includes indexes, constraints, comments

2. **`django_app/apps/*/models.py`** (Django Models)
   - Django ORM models
   - Generates migrations
   - Must match canonical schema

3. **`src/database/models.py`** (SQLAlchemy Models)
   - FastAPI SQLAlchemy models
   - Must mirror Django models
   - Used by FastAPI application

### Generated/Exported Files

4. **`scripts/database/schema_sqlalchemy.sql`**
   - Auto-generated from SQLAlchemy models
   - For reference only (not source of truth)
   - Regenerated with: `./scripts/database/export_schema.sh`

5. **`scripts/database/schema_django.sql`**
   - Auto-generated from Django migrations
   - For reference only (not source of truth)
   - Regenerated with: `./scripts/database/export_schema.sh`

## Version Tracking

All schema changes must be documented in `schema_canonical.sql`:

```sql
-- Version 1.1.0 (2026-01-15)
--   - Added market_cap column to stocks table
--   - Added index on market_cap
--   - Migration: django_app/apps/options/migrations/0002_add_market_cap.py
```

## Best Practices

### 1. Always Start with Canonical Schema

**❌ Wrong:**
```python
# Don't add fields to Django models first
class Stock(models.Model):
    new_field = models.CharField(max_length=100)  # Wrong!
```

**✅ Correct:**
```sql
-- Update canonical schema first
ALTER TABLE stocks ADD COLUMN new_field VARCHAR(100);
```

Then update Django and SQLAlchemy models.

### 2. Use Idempotent SQL

Always use `IF NOT EXISTS` and `IF EXISTS`:

```sql
-- ✅ Good
CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol);

-- ❌ Bad
CREATE INDEX idx_stocks_symbol ON stocks(symbol);  -- Fails if exists
```

### 3. Document Changes

Always update the version tracking section:

```sql
-- Version 1.2.0 (2026-02-01)
--   - Added expiration_date to option_contracts
--   - Changed option_type from VARCHAR(4) to VARCHAR(10)
--   - Migration: django_app/apps/options/migrations/0003_update_option_contracts.py
```

### 4. Test Migrations

Before applying to production:

```bash
# Test on development database
python manage.py migrate

# Verify schema matches
./scripts/database/verify_schema.py
```

### 5. Keep All Three in Sync

After any change, verify:
- ✅ Canonical schema updated
- ✅ Django models updated
- ✅ SQLAlchemy models updated
- ✅ Migrations generated
- ✅ All tests pass

## Common Operations

### Adding a New Table

1. Add to `schema_canonical.sql`:
```sql
CREATE TABLE IF NOT EXISTS new_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

2. Add Django model:
```python
class NewTable(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
```

3. Add SQLAlchemy model:
```python
class NewTable(Base):
    __tablename__ = 'new_table'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### Adding a Column

1. Update `schema_canonical.sql`:
```sql
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS new_column VARCHAR(50);
```

2. Update Django model:
```python
new_column = models.CharField(max_length=50, null=True, blank=True)
```

3. Update SQLAlchemy model:
```python
new_column = Column(String(50), nullable=True)
```

### Adding an Index

1. Update `schema_canonical.sql`:
```sql
CREATE INDEX IF NOT EXISTS idx_stocks_new_column ON stocks(new_column);
```

2. Update Django model Meta:
```python
class Meta:
    indexes = [
        models.Index(fields=['new_column'], name='idx_stocks_new_column'),
    ]
```

3. Update SQLAlchemy model:
```python
__table_args__ = (
    Index('idx_stocks_new_column', 'new_column'),
)
```

## Verification

### Automated Verification

```bash
# Verify schema matches models
./scripts/database/verify_schema.py

# Export and compare schemas
./scripts/database/export_schema.sh
diff scripts/database/schema_canonical.sql scripts/database/schema_sqlalchemy.sql
```

### Manual Verification

1. Check canonical schema is up to date
2. Compare Django models with canonical schema
3. Compare SQLAlchemy models with canonical schema
4. Run Django migrations to ensure they match
5. Run tests to ensure everything works

## Troubleshooting

### Schema Drift

If schemas get out of sync:

1. **Identify the difference:**
   ```bash
   ./scripts/database/export_schema.sh
   diff scripts/database/schema_canonical.sql scripts/database/schema_sqlalchemy.sql
   ```

2. **Fix canonical schema first** (source of truth)

3. **Update Django models** to match

4. **Update SQLAlchemy models** to match

5. **Regenerate migrations** if needed

### Migration Conflicts

If Django migrations conflict:

1. Check canonical schema for the intended state
2. Create a new migration that matches canonical schema
3. Update SQLAlchemy models to match
4. Test thoroughly before applying

## Summary

**Remember:**
- ⭐ `schema_canonical.sql` is the **SINGLE SOURCE OF TRUTH**
- Always update canonical schema first
- Then update Django models
- Then update SQLAlchemy models
- Verify all three are in sync
- Document all changes in version tracking

