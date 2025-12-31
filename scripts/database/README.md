# Database Setup Scripts

Scripts for setting up PostgreSQL + TimescaleDB and running migrations.

## Setup Process

### 1. Install PostgreSQL + TimescaleDB (APP-SERVER)

On APP-SERVER (10.0.0.80), run:

```bash
sudo ./scripts/database/setup_postgresql.sh
```

This will:
- Install PostgreSQL
- Install TimescaleDB extension
- Create `options_db` database
- Create `bifrost` user
- Configure TimescaleDB

**Important**: Update the password in your `.env` file after running this script.

### 2. Configure Environment Variables

Create or update `.env` file in project root:

```env
# Database (shared)
DB_NAME=options_db
DB_USER=bifrost
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
```

### 3. Run Django Migrations

From project root:

```bash
./scripts/database/run_migrations.sh
```

Or manually:

```bash
cd django_app
python manage.py makemigrations
python manage.py migrate
```

### 4. Set Up TimescaleDB Hypertables

After migrations, convert `option_snapshots` to a hypertable:

```bash
psql -U bifrost -d options_db -f scripts/database/setup_timescaledb.sql
```

Or manually:

```bash
psql -U bifrost -d options_db
\i scripts/database/setup_timescaledb.sql
```

### 5. Test Connections

Test both Django and FastAPI database connections:

```bash
python scripts/database/test_connection.py
```

## Files

- `setup_postgresql.sh` - PostgreSQL + TimescaleDB installation script
- `setup_timescaledb.sql` - SQL script to create hypertables
- `run_migrations.sh` - Django migration runner
- `test_connection.py` - Connection test script

## Manual Setup (Alternative)

If you prefer manual setup:

### Install PostgreSQL

```bash
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib
```

### Install TimescaleDB

```bash
# Add TimescaleDB repository
sh -c "echo 'deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main' > /etc/apt/sources.list.d/timescaledb.list"
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y timescaledb-2-postgresql-14

# Configure
sudo timescaledb-tune --quiet --yes
sudo systemctl restart postgresql
```

### Create Database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE options_db;
CREATE USER bifrost WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE options_db TO bifrost;
\c options_db
CREATE EXTENSION IF NOT EXISTS timescaledb;
GRANT ALL ON SCHEMA public TO bifrost;
```

## Troubleshooting

### Connection Refused

- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Check firewall rules
- Verify DB_HOST in .env file

### Authentication Failed

- Verify DB_USER and DB_PASSWORD in .env
- Check pg_hba.conf for authentication method
- Verify user exists: `sudo -u postgres psql -c "\du"`

### TimescaleDB Not Found

- Verify extension is installed: `psql -U bifrost -d options_db -c "SELECT * FROM pg_extension WHERE extname = 'timescaledb';"`
- Reinstall if needed: `sudo apt-get install --reinstall timescaledb-2-postgresql-14`

### Migration Errors

- Check database user has proper permissions
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Django settings for correct database configuration

## Next Steps

After database setup:

1. Create Django superuser: `python manage.py createsuperuser`
2. Test data collection: `python manage.py collect_options SPY`
3. Start Celery worker: `celery -A services.celery_app worker --loglevel=info`
4. Test FastAPI endpoints with database

