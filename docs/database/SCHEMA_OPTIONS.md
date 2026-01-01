# Options App - Database Schema

Stock symbols, option snapshots, and option contracts

> **Note:** This is an auto-generated file. The source of truth is Django models (`app_django/apps/*/models.py`).
> 
> For the raw SQL schema files, see the app-specific schema files in `scripts/database/`.

---

## Tables

### option_contracts

**Description:** option_contracts table

**Columns:**

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

**Foreign Keys:**

- `snapshot_id` → `option_snapshots.id`

**Indexes:**

- `snapshot_id`
- `symbol`
- `timestamp`
- `expiration`
- `strike`

---

### option_snapshots

**Description:** option_snapshots table

**Columns:**

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

**Foreign Keys:**

- `stock_id` → `stocks.id`

**Indexes:**

- `stock_id`
- `symbol`
- `timestamp`

---

### stocks

**Description:** stocks table

**Columns:**

| Column Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | `SERIAL` | PRIMARY KEY | Primary key |
| `symbol` | `VARCHAR(10)` | NOT NULL, UNIQUE | Text field |
| `name` | `VARCHAR(200)` | - | Text field |
| `sector` | `VARCHAR(100)` | - | Text field |
| `industry` | `VARCHAR(100)` | - | Text field |
| `created_at` | `TIMESTAMP WITH` | HAS DEFAULT | Timestamp |
| `updated_at` | `TIMESTAMP WITH` | HAS DEFAULT | Timestamp |

**Indexes:**

- `symbol`
- `created_at`

---

## Related Files

- **Django Models**: `app_django/apps/options/models.py` (Single Source of Truth)
- **SQLAlchemy Models**: `src/database/models.py`
- **SQL Schema File**: `scripts/database/schema_options.sql`

## Navigation

- [← Back to Schema Overview](SCHEMA.md)

---

**Last Updated**: Auto-generated from schema files
