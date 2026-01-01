# Complete Database Schema

This document provides a human-readable view of the complete database schema.

> **Note:** This is an auto-generated file. The source of truth is Django models (`app_django/apps/*/models.py`).
> 
> For the raw SQL schema, see: [schema_all.sql](schema_all.sql)

## Schema Overview

The database schema is organized into three Django apps:

- **Options App**: Stock symbols, option snapshots, and option contracts
- **Strategies App**: Strategy history and market conditions
- **Data Collection App**: Collection job tracking

---

## collection_jobs

**Description:** collection_jobs table

### Columns

| Column Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | `SERIAL` | PRIMARY KEY | Primary key |
| `job_type` | `VARCHAR(50)` | NOT NULL | Categorical value |
| `symbol` | `VARCHAR(10)` | - | Text field |
| `status` | `VARCHAR(20)` | NOT NULL | Categorical value |
| `started_at` | `TIMESTAMP WITH` | - | Timestamp |
| `completed_at` | `TIMESTAMP WITH` | - | Timestamp |
| `created_at` | `TIMESTAMP WITH` | HAS DEFAULT | Timestamp |
| `records_collected` | `INTEGER` | - | Integer count |
| `error_message` | `TEXT` | - | Text field |

### Indexes

- `status`
- `job_type`
- `symbol`
- `created_at`

---

## market_conditions

**Description:** market_conditions table

### Columns

| Column Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | `SERIAL` | PRIMARY KEY | Primary key |
| `timestamp` | `TIMESTAMP WITH` | NOT NULL, HAS DEFAULT | Timestamp |
| `sp500_price` | `DOUBLE PRECISION` | - | Price/numeric value |
| `vix` | `DOUBLE PRECISION` | - | Option Greek / Volatility |
| `market_trend` | `VARCHAR(20)` | - | Categorical value |
| `volatility_regime` | `VARCHAR(20)` | - | Categorical value |
| `meta_data` | `JSONB` | - | JSON data |

### Indexes

- `timestamp`

---

## option_contracts

**Description:** option_contracts table

### Columns

| Column Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | `SERIAL` | PRIMARY KEY | Primary key |
| `snapshot_id` | `INTEGER` | NOT NULL | Foreign key reference |
| `symbol` | `VARCHAR(10)` | NOT NULL | Text field |
| `strike` | `DOUBLE PRECISION` | NOT NULL | Price/numeric value |
| `expiration` | `VARCHAR(8)` | NOT NULL | - |
| `option_type` | `VARCHAR(4)` | NOT NULL | Categorical value |
| `bid` | `DOUBLE PRECISION` | NOT NULL | Price/numeric value |
| `ask` | `DOUBLE PRECISION` | NOT NULL | Price/numeric value |
| `last` | `DOUBLE PRECISION` | - | - |
| `mid_price` | `DOUBLE PRECISION` | - | - |
| `volume` | `INTEGER` | - | Integer count |
| `open_interest` | `INTEGER` | - | Integer count |
| `implied_volatility` | `DOUBLE PRECISION` | - | Option Greek / Volatility |
| `delta` | `DOUBLE PRECISION` | - | Option Greek / Volatility |
| `gamma` | `DOUBLE PRECISION` | - | Option Greek / Volatility |
| `theta` | `DOUBLE PRECISION` | - | Option Greek / Volatility |
| `vega` | `DOUBLE PRECISION` | - | Option Greek / Volatility |
| `contract_id` | `INTEGER` | UNIQUE | Foreign key reference |
| `timestamp` | `TIMESTAMP WITH` | NOT NULL | Timestamp |
| `created_at` | `TIMESTAMP WITH` | HAS DEFAULT | Timestamp |

### Foreign Keys

- `snapshot_id` → `option_snapshots.id`

### Indexes

- `snapshot_id`
- `symbol`
- `timestamp`
- `expiration`
- `strike`

---

## option_snapshots

**Description:** option_snapshots table

### Columns

| Column Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | `SERIAL` | PRIMARY KEY | Primary key |
| `stock_id` | `INTEGER` | NOT NULL | Foreign key reference |
| `symbol` | `VARCHAR(10)` | NOT NULL | Text field |
| `underlying_price` | `DOUBLE PRECISION` | NOT NULL | Price/numeric value |
| `timestamp` | `TIMESTAMP WITH` | NOT NULL | Timestamp |
| `contracts_data` | `JSONB` | - | JSON data |
| `expiration_dates` | `JSONB` | - | JSON data |
| `strike_range` | `JSONB` | - | JSON data |
| `created_at` | `TIMESTAMP WITH` | HAS DEFAULT | Timestamp |

### Foreign Keys

- `stock_id` → `stocks.id`

### Indexes

- `stock_id`
- `symbol`
- `timestamp`

---

## stocks

**Description:** stocks table

### Columns

| Column Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | `SERIAL` | PRIMARY KEY | Primary key |
| `symbol` | `VARCHAR(10)` | NOT NULL, UNIQUE | Text field |
| `name` | `VARCHAR(200)` | - | Text field |
| `sector` | `VARCHAR(100)` | - | Text field |
| `industry` | `VARCHAR(100)` | - | Text field |
| `created_at` | `TIMESTAMP WITH` | HAS DEFAULT | Timestamp |
| `updated_at` | `TIMESTAMP WITH` | HAS DEFAULT | Timestamp |

### Indexes

- `symbol`
- `created_at`

---

## strategy_history

**Description:** strategy_history table

### Columns

| Column Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | `SERIAL` | PRIMARY KEY | Primary key |
| `stock_id` | `INTEGER` | NOT NULL | Foreign key reference |
| `symbol` | `VARCHAR(10)` | NOT NULL | Text field |
| `strategy_type` | `VARCHAR(50)` | NOT NULL | Categorical value |
| `parameters` | `JSONB` | - | JSON data |
| `entry_cost` | `DOUBLE PRECISION` | NOT NULL | Price/numeric value |
| `max_profit` | `DOUBLE PRECISION` | NOT NULL | Price/numeric value |
| `max_loss` | `DOUBLE PRECISION` | NOT NULL | Price/numeric value |
| `breakeven_points` | `JSONB` | - | JSON data |
| `profit_profile` | `JSONB` | - | JSON data |
| `delta` | `DOUBLE PRECISION` | - | Option Greek / Volatility |
| `gamma` | `DOUBLE PRECISION` | - | Option Greek / Volatility |
| `theta` | `DOUBLE PRECISION` | - | Option Greek / Volatility |
| `vega` | `DOUBLE PRECISION` | - | Option Greek / Volatility |
| `probability_of_profit` | `DOUBLE PRECISION` | - | - |
| `risk_reward_ratio` | `DOUBLE PRECISION` | - | - |
| `timestamp` | `TIMESTAMP WITH` | NOT NULL | Timestamp |
| `created_at` | `TIMESTAMP WITH` | HAS DEFAULT | Timestamp |

### Foreign Keys

- `stock_id` → `stocks.id`

### Indexes

- `stock_id`
- `symbol`
- `strategy_type`
- `timestamp`
- `created_at`

---

## Related Files

- **Django Models**: `app_django/apps/*/models.py` (Single Source of Truth)
- **SQLAlchemy Models**: `src/database/models.py`
- **Raw SQL Schema**: [schema_all.sql](schema_all.sql)
- **App-Specific Schemas**:
  - [schema_options.sql](../../scripts/database/schema_options.sql)
  - [schema_strategies.sql](../../scripts/database/schema_strategies.sql)
  - [schema_data_collection.sql](../../scripts/database/schema_data_collection.sql)

## Regenerating This Documentation

This documentation is auto-generated from `schema_all.sql`. To regenerate:

```bash
./scripts/database/refresh_schema.sh
```

This single command will:
1. Combine all app-specific schema files into `schema_all.sql`
2. Generate this markdown documentation

---

**Last Updated**: Auto-generated from schema files
