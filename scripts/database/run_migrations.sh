#!/bin/bash
# Run Django migrations to create database schema
# Run this from the project root directory

set -e

echo "=========================================="
echo "Bifrost Database Migration Script"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found."
    echo "Please create .env file with database credentials."
    echo ""
    echo "Example .env content:"
    echo "  DB_NAME=options_db"
    echo "  DB_USER=bifrost"
    echo "  DB_PASSWORD=your_password"
    echo "  DB_HOST=localhost"
    echo "  DB_PORT=5432"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Change to django_app directory
cd django_app

echo "Creating migrations..."
python manage.py makemigrations

echo ""
echo "Applying migrations..."
python manage.py migrate

echo ""
echo "=========================================="
echo "Migrations complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Set up TimescaleDB hypertables:"
echo "   psql -U bifrost -d options_db -f ../scripts/database/setup_timescaledb.sql"
echo ""
echo "2. Create Django superuser (optional):"
echo "   python manage.py createsuperuser"
echo ""

