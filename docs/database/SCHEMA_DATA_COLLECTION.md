# Data Collection

Collection job tracking

> **Note:** This is an auto-generated file. The source of truth is Django models (`app_django/apps/*/models.py`).
> 
> For the raw SQL schema files, see the app-specific schema files in `scripts/database/`.

---

## Tables

### collection_jobs

**Description:** collection_jobs table

**Columns:**

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

**Indexes:**

- `status`
- `job_type`
- `symbol`
- `created_at`

---

## Related Files

- **Django Models**: `app_django/apps/data_collection/models.py` (Single Source of Truth)
- **SQLAlchemy Models**: `src/database/models.py`
- **SQL Schema File**: `scripts/database/schema_data_collection.sql`

## Navigation

- [← Back to Schema Overview](SCHEMA.md)

---

**Last Updated**: Auto-generated from schema files
