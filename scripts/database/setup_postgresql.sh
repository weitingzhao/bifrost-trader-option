#!/bin/bash
# PostgreSQL + TimescaleDB setup script for APP-SERVER (10.0.0.80)
# Run this script on APP-SERVER as root or with sudo

set -e

echo "=========================================="
echo "Bifrost PostgreSQL + TimescaleDB Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

# Update package list
echo "Updating package list..."
apt-get update

# Install PostgreSQL
echo "Installing PostgreSQL..."
apt-get install -y postgresql postgresql-contrib

# Install TimescaleDB
echo "Installing TimescaleDB..."
# Add TimescaleDB repository
sh -c "echo 'deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main' > /etc/apt/sources.list.d/timescaledb.list"
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | apt-key add -
apt-get update
apt-get install -y timescaledb-2-postgresql-14

# Configure TimescaleDB
echo "Configuring TimescaleDB..."
timescaledb-tune --quiet --yes

# Start and enable PostgreSQL
echo "Starting PostgreSQL service..."
systemctl start postgresql
systemctl enable postgresql

# Create database and user
echo "Creating database and user..."
sudo -u postgres psql <<EOF
-- Create database
CREATE DATABASE options_db;

-- Create user
CREATE USER bifrost WITH PASSWORD 'CHANGE_THIS_PASSWORD';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE options_db TO bifrost;

-- Connect to database and set up TimescaleDB
\c options_db
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO bifrost;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO bifrost;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO bifrost;
EOF

echo ""
echo "=========================================="
echo "PostgreSQL + TimescaleDB setup complete!"
echo "=========================================="
echo ""
echo "IMPORTANT: Update the password in your .env file:"
echo "  DB_PASSWORD=CHANGE_THIS_PASSWORD"
echo ""
echo "Next steps:"
echo "1. Update .env file with database credentials"
echo "2. Run Django migrations: cd django_app && python manage.py makemigrations"
echo "3. Run migrations: python manage.py migrate"
echo "4. Set up TimescaleDB hypertables (see scripts/database/setup_timescaledb.sql)"

