# Schema Summary

This document provides a human-readable view of the complete database schema.

> **Note:** This is an auto-generated file. The source of truth is Django models (`app_django/apps/*/models.py`).
> 
> For the raw SQL schema files, see the app-specific schema files in `scripts/database/`.

## Schema Overview

The database schema is organized into three Django apps:

- **[Options App](SCHEMA_OPTIONS.md)**: Stock symbols, option snapshots, and option contracts
- **[Strategies App](SCHEMA_STRATEGIES.md)**: Strategy history and market conditions
- **[Data Collection App](SCHEMA_DATA_COLLECTION.md)**: Collection job tracking

---

## App-Specific Schema Documentation

Click on the links above to view detailed schema documentation for each Django app.

---

## Related Files

- **Django Models**: `app_django/apps/*/models.py` (Single Source of Truth)
- **SQLAlchemy Models**: `src/database/models.py`
- **App-Specific SQL Schema Files** (in `scripts/database/`):
  - `schema_options.sql` - Options app tables
  - `schema_strategies.sql` - Strategies app tables
  - `schema_data_collection.sql` - Data collection app tables

## Regenerating This Documentation

This documentation is auto-generated from `schema_*.sql` files. To regenerate:

```bash
./scripts/database/refresh_schema.sh
```

This command will:
1. Read all `schema_*.sql` files directly
2. Generate markdown documentation for each app
3. Verify schema synchronization (Django → SQLAlchemy → schema files)

---

**Last Updated**: Auto-generated from schema files
