# Strategies App - Database Schema

Strategy history and market conditions

> **Note:** This is an auto-generated file. The source of truth is Django models (`app_django/apps/*/models.py`).
> 
> For the raw SQL schema files, see the app-specific schema files in `scripts/database/`.

---

## Tables

### market_conditions

**Description:** market_conditions table

**Columns:**

| Column Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | `SERIAL` | PRIMARY KEY | Primary key |
| `timestamp` | `TIMESTAMP WITH` | NOT NULL, HAS DEFAULT | Timestamp |
| `sp500_price` | `DOUBLE PRECISION` | - | Price/numeric value |
| `vix` | `DOUBLE PRECISION` | - | Option Greek / Volatility |
| `market_trend` | `VARCHAR(20)` | - | Categorical value |
| `volatility_regime` | `VARCHAR(20)` | - | Categorical value |
| `meta_data` | `JSONB` | - | JSON data |

**Indexes:**

- `timestamp`

---

### strategy_history

**Description:** strategy_history table

**Columns:**

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

**Foreign Keys:**

- `stock_id` → `stocks.id`

**Indexes:**

- `stock_id`
- `symbol`
- `strategy_type`
- `timestamp`
- `created_at`

---

## Related Files

- **Django Models**: `app_django/apps/strategies/models.py` (Single Source of Truth)
- **SQLAlchemy Models**: `src/database/models.py`
- **SQL Schema File**: `scripts/database/schema_strategies.sql`

## Navigation

- [← Back to Schema Overview](SCHEMA.md)

---

**Last Updated**: Auto-generated from schema files
