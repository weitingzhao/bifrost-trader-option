# Database Documentation

This directory contains all database-related documentation for the Bifrost project.

## Single Source of Truth

**`app_django/apps/*/models.py`** (Django Models) is the **single source of truth** for the database schema.

Django models define the authoritative database schema. All other schema representations (SQLAlchemy models and schema.sql) must match Django models.

## Schema Change Process

### Workflow for Database Changes

When making any database schema changes, follow this process:

```
1. Update Django models (app_django/apps/*/models.py) ⭐ SINGLE SOURCE OF TRUTH
   ↓
2. Generate Django migrations (python manage.py makemigrations)
   ↓
3. Update SQLAlchemy models (src/database/models.py) to match Django models
   ↓
4. Update scripts/database/schema.sql to match Django models
   ↓
5. Run verify_schema.py to verify all three are in sync
```

### Step-by-Step Process

#### 1. Update Django Models ⭐ SINGLE SOURCE OF TRUTH

Edit the appropriate Django model file:
- `app_django/apps/options/models.py` - For stocks, option_snapshots, option_contracts
- `app_django/apps/strategies/models.py` - For strategy_history, market_conditions
- `app_django/apps/data_collection/models.py` - For collection_jobs

```python
class Stock(models.Model):
    # ... existing fields ...
    market_cap = models.BigIntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'stocks'
        indexes = [
            models.Index(fields=['market_cap'], name='idx_stocks_market_cap'),
        ]
```

**Important:**
- Django models are the authoritative source
- All changes start here
- Use proper Django field types and constraints
- Document changes in migration files

#### 2. Generate Django Migrations

```bash
cd app_django
python manage.py makemigrations
python manage.py migrate
```

This creates migration files in `app_django/apps/*/migrations/`.

**Note:** Review the generated migration to ensure it matches your intended changes.

#### 3. Update SQLAlchemy Models

Edit `src/database/models.py` to match Django models exactly:

```python
class Stock(Base):
    """Stock symbol and metadata (mirrors Django apps.options.models.Stock)."""
    __tablename__ = 'stocks'
    
    # ... existing fields ...
    market_cap = Column(BigInteger, nullable=True)
    
    __table_args__ = (
        Index('idx_stocks_market_cap', 'market_cap'),
    )
```

**Important:**
- Must mirror Django models exactly
- Match field types, constraints, and indexes
- Keep `__tablename__` matching Django's `db_table`
- Update docstrings to reference Django model

#### 4. Update Schema SQL

Edit `scripts/database/schema.sql` to match Django models:

```sql
-- Update to match Django model changes
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS market_cap BIGINT;
CREATE INDEX IF NOT EXISTS idx_stocks_market_cap ON stocks(market_cap);
```

**Important:**
- Use `IF NOT EXISTS` for idempotent operations
- Document changes in version tracking section
- Include comments for new tables/columns
- Keep in sync with Django migrations

#### 5. Verify Synchronization

Run the verification script to ensure all three are in sync:

```bash
./scripts/database/verify_schema.py
```

This script compares:
- Django models (`app_django/apps/*/models.py`)
- SQLAlchemy models (`src/database/models.py`)
- Schema SQL (`scripts/database/schema.sql`)

**Expected output:** All three should match. If not, fix discrepancies starting from Django models (source of truth).

## Schema Files

### Primary Files

1. **`app_django/apps/*/models.py`** ⭐ **SINGLE SOURCE OF TRUTH** (Django Models)
   - Django ORM models
   - Authoritative schema definition
   - All changes start here
   - Generates migrations automatically
   - Used by Django admin and management commands

2. **`src/database/models.py`** (SQLAlchemy Models)
   - FastAPI SQLAlchemy models
   - Must mirror Django models exactly
   - Used by FastAPI application for async operations
   - Updated after Django models change

3. **`scripts/database/schema.sql`** (Reference Schema)
   - SQL representation of the schema
   - Must match Django models
   - Updated after Django models change
   - Used for documentation and reference
   - Includes indexes, constraints, comments

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

All schema changes are tracked in Django migrations:

```python
# app_django/apps/options/migrations/0002_add_market_cap.py
class Migration(migrations.Migration):
    dependencies = [
        ('options', '0001_initial'),
    ]
    operations = [
        migrations.AddField(
            model_name='stock',
            name='market_cap',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name='stock',
            index=models.Index(fields=['market_cap'], name='idx_stocks_market_cap'),
        ),
    ]
```

**Optional:** Document changes in `scripts/database/schema.sql` version tracking section for reference:

```sql
-- Version 1.1.0 (2026-01-15)
--   - Added market_cap column to stocks table
--   - Added index on market_cap
--   - Migration: app_django/apps/options/migrations/0002_add_market_cap.py
```

## Best Practices

### 1. Always Start with Django Models

**✅ Correct:**
```python
# Update Django models first (SINGLE SOURCE OF TRUTH)
class Stock(models.Model):
    new_field = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        db_table = 'stocks'
```

**Then:**
1. Generate Django migrations
2. Update SQLAlchemy models to match
3. Update schema.sql to match
4. Run verify_schema.py to verify sync

### 2. Review Generated Migrations

Always review Django migrations before applying:

```bash
cd app_django
python manage.py makemigrations
# Review the generated migration file
python manage.py migrate
```

### 3. Keep All Three in Sync

After updating Django models:
1. ✅ Generate and review Django migrations
2. ✅ Update SQLAlchemy models to match
3. ✅ Update schema.sql to match
4. ✅ Run verify_schema.py to verify sync

### 4. Test Migrations

Before applying to production:

```bash
# Test on development database
cd app_django
python manage.py migrate

# Verify all three are in sync
./scripts/database/verify_schema.py
```

### 5. Use Idempotent SQL in schema.sql

When updating `scripts/database/schema.sql`, always use `IF NOT EXISTS` and `IF EXISTS`:

```sql
-- ✅ Good
CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol);
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS new_field VARCHAR(100);

-- ❌ Bad
CREATE INDEX idx_stocks_symbol ON stocks(symbol);  -- Fails if exists
```

## Common Operations

### Adding a New Table

1. **Add Django model** (SINGLE SOURCE OF TRUTH):
```python
# app_django/apps/options/models.py (or appropriate app)
class NewTable(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'new_table'
```

2. **Generate Django migrations:**
```bash
cd app_django
python manage.py makemigrations
python manage.py migrate
```

3. **Add SQLAlchemy model** to match:
```python
# src/database/models.py
class NewTable(Base):
    """New table (mirrors Django apps.options.models.NewTable)."""
    __tablename__ = 'new_table'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

4. **Update schema.sql** to match:
```sql
CREATE TABLE IF NOT EXISTS new_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

5. **Verify synchronization:**
```bash
./scripts/database/verify_schema.py
```

### Adding a Column

1. **Update Django model** (SINGLE SOURCE OF TRUTH):
```python
# app_django/apps/options/models.py
class Stock(models.Model):
    # ... existing fields ...
    new_column = models.CharField(max_length=50, null=True, blank=True)
```

2. **Generate Django migrations:**
```bash
cd app_django
python manage.py makemigrations
python manage.py migrate
```

3. **Update SQLAlchemy model** to match:
```python
# src/database/models.py
class Stock(Base):
    # ... existing fields ...
    new_column = Column(String(50), nullable=True)
```

4. **Update schema.sql** to match:
```sql
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS new_column VARCHAR(50);
```

5. **Verify synchronization:**
```bash
./scripts/database/verify_schema.py
```

### Adding an Index

1. **Update Django model** (SINGLE SOURCE OF TRUTH):
```python
# app_django/apps/options/models.py
class Stock(models.Model):
    # ... existing fields ...
    
    class Meta:
        db_table = 'stocks'
        indexes = [
            models.Index(fields=['new_column'], name='idx_stocks_new_column'),
        ]
```

2. **Generate Django migrations:**
```bash
cd app_django
python manage.py makemigrations
python manage.py migrate
```

3. **Update SQLAlchemy model** to match:
```python
# src/database/models.py
class Stock(Base):
    # ... existing fields ...
    
    __table_args__ = (
        Index('idx_stocks_new_column', 'new_column'),
    )
```

4. **Update schema.sql** to match:
```sql
CREATE INDEX IF NOT EXISTS idx_stocks_new_column ON stocks(new_column);
```

5. **Verify synchronization:**
```bash
./scripts/database/verify_schema.py
```

## Verification

### Automated Verification

```bash
# Verify schema matches models
./scripts/database/verify_schema.py

# Export and compare schemas
./scripts/database/export_schema.sh
diff scripts/database/schema.sql scripts/database/schema_sqlalchemy.sql
```

### Manual Verification

1. Check Django models are up to date (source of truth)
2. Compare SQLAlchemy models with Django models
3. Compare schema.sql with Django models
4. Run Django migrations to ensure database matches models
5. Run tests to ensure everything works

## Troubleshooting

### Schema Drift

If schemas get out of sync:

1. **Identify the difference:**
   ```bash
   ./scripts/database/verify_schema.py
   ```

2. **Fix Django models first** (source of truth)
   - Update Django models to desired state
   - Generate new migrations if needed

3. **Update SQLAlchemy models** to match Django models

4. **Update schema.sql** to match Django models

5. **Verify synchronization:**
   ```bash
   ./scripts/database/verify_schema.py
   ```

### Migration Conflicts

If Django migrations conflict:

1. **Resolve conflicts in Django migrations:**
   ```bash
   cd app_django
   python manage.py makemigrations --merge
   ```

2. **Review and adjust migrations** to match your intended schema

3. **Update SQLAlchemy models** to match Django models

4. **Update schema.sql** to match Django models

5. **Test thoroughly before applying:**
   ```bash
   python manage.py migrate
   ./scripts/database/verify_schema.py
   ```

## Summary

**Remember:**
- ⭐ `app_django/apps/*/models.py` (Django Models) is the **SINGLE SOURCE OF TRUTH**
- Always update Django models first
- Generate Django migrations
- Then update SQLAlchemy models to match Django models
- Then update schema.sql to match Django models
- Run `verify_schema.py` to verify all three are in sync
- Django migrations track all schema changes

