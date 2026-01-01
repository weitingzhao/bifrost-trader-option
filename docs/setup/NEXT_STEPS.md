# Next Steps - Implementation Guide

## Phase 1 Complete ✅

All Phase 1 foundation tasks are complete. The codebase is ready for database setup and testing.

## Immediate Next Steps

### 1. Install Dependencies

**On Dev PC (10.0.0.90):**

```bash
# Install Python dependencies
./scripts/setup/install_dependencies.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set Up Database (APP-SERVER)

**On APP-SERVER (10.0.0.80):**

```bash
# SSH to APP-SERVER
ssh user@10.0.0.80

# Run PostgreSQL + TimescaleDB setup
sudo ./scripts/database/setup_postgresql.sh

# Update .env file with database password
nano .env  # Update DB_PASSWORD
```

### 3. Configure Environment Variables

**Create .env file from example:**

```bash
cp .env.example .env
nano .env  # Update all values, especially:
           # - DB_PASSWORD
           # - DJANGO_SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_urlsafe(50))")
```

### 4. Run Database Migrations

**On APP-SERVER:**

```bash
# Run migrations
./scripts/database/run_migrations.sh

# Or manually:
cd app_django
python manage.py makemigrations
python manage.py migrate
```

### 5. Set Up TimescaleDB Hypertables

**On APP-SERVER:**

```bash
psql -U bifrost -d options_db -f scripts/database/setup_timescaledb.sql
```

### 6. Test Database Connections

**On APP-SERVER:**

```bash
python scripts/database/test_connection.py
```

### 7. Create Django Superuser (Optional)

**On APP-SERVER:**

```bash
cd app_django
python manage.py createsuperuser
```

### 8. Test Services

**On APP-SERVER:**

```bash
# Test FastAPI
python3 -m src.api.main
# Should start on http://0.0.0.0:8000

# Test Django
cd app_django
python manage.py runserver 0.0.0.0:8001
# Should start on http://0.0.0.0:8001

# Test Celery (in another terminal)
celery -A services.celery_app worker --loglevel=info

# Test data collection
python manage.py collect_options SPY
```

## Quick Start Checklist

- [ ] Install dependencies (`./scripts/setup/install_dependencies.sh`)
- [ ] Set up PostgreSQL + TimescaleDB on APP-SERVER
- [ ] Create `.env` file from `.env.example`
- [ ] Update `.env` with database credentials
- [ ] Run Django migrations
- [ ] Set up TimescaleDB hypertables
- [ ] Test database connections
- [ ] Create Django superuser
- [ ] Test FastAPI service
- [ ] Test Django admin
- [ ] Test data collection

## Scripts Available

### Setup Scripts
- `scripts/setup/install_dependencies.sh` - Install Python dependencies
- `scripts/database/setup_postgresql.sh` - PostgreSQL + TimescaleDB setup
- `scripts/database/run_migrations.sh` - Run Django migrations
- `scripts/database/test_connection.py` - Test database connections

### Database Scripts
- `scripts/database/setup_timescaledb.sql` - TimescaleDB hypertable setup

## Documentation

- `scripts/database/README.md` - Detailed database setup guide
- `docs/PROJECT_PLAN.md` - Complete project plan
- `PHASE1_STATUS.md` - Phase 1 completion status

## Troubleshooting

### Dependencies Not Installing

```bash
# Make sure you're using Python 3.9+
python3 --version

# Try upgrading pip
pip install --upgrade pip

# Install specific problematic packages separately
pip install psycopg2-binary
pip install asyncpg
```

### Database Connection Issues

1. Check PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify `.env` file has correct credentials
3. Test connection: `psql -U bifrost -d options_db -h localhost`
4. Check firewall rules if connecting remotely

### Migration Errors

1. Ensure database exists: `psql -U postgres -l`
2. Check user permissions: `psql -U postgres -c "\du"`
3. Verify Django settings: `python manage.py check`

## Phase 2 Preparation

Once database is set up:

1. Test data collection service
2. Verify option chain storage
3. Test historical data endpoints
4. Set up scheduled data collection
5. Monitor data collection jobs

## Support

For issues or questions:
- Check `scripts/database/README.md` for database setup
- Review `docs/PROJECT_PLAN.md` for architecture details
- Check service logs for errors

