#!/usr/bin/env python3
"""Test database connections for both FastAPI and Django."""
import sys
import os
import asyncio

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_django_connection():
    """Test Django database connection."""
    print("Testing Django database connection...")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_config.settings')
        import django
        django.setup()
        
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✓ Django connection successful!")
            print(f"  PostgreSQL version: {version[0]}")
            
            # Check TimescaleDB extension
            cursor.execute("SELECT * FROM pg_extension WHERE extname = 'timescaledb';")
            if cursor.fetchone():
                print("✓ TimescaleDB extension is installed")
            else:
                print("⚠ TimescaleDB extension not found")
                
        return True
    except Exception as e:
        print(f"✗ Django connection failed: {e}")
        return False


async def test_fastapi_connection():
    """Test FastAPI (SQLAlchemy) database connection."""
    print("\nTesting FastAPI (SQLAlchemy) database connection...")
    try:
        from src.database.connection import get_engine, Base
        from src.database.models import Stock, OptionSnapshot
        
        engine = get_engine()
        
        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute("SELECT version();")
            version = result.scalar()
            print(f"✓ FastAPI connection successful!")
            print(f"  PostgreSQL version: {version}")
            
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(engine.sync_engine)
            tables = inspector.get_table_names()
            print(f"  Found {len(tables)} tables in database")
            
            if 'stocks' in tables:
                print("✓ Stocks table exists")
            if 'option_snapshots' in tables:
                print("✓ Option snapshots table exists")
                
        return True
    except Exception as e:
        print(f"✗ FastAPI connection failed: {e}")
        return False


def main():
    """Run all connection tests."""
    print("=" * 50)
    print("Bifrost Database Connection Test")
    print("=" * 50)
    print("")
    
    # Test Django
    django_ok = test_django_connection()
    
    # Test FastAPI
    fastapi_ok = asyncio.run(test_fastapi_connection())
    
    print("")
    print("=" * 50)
    if django_ok and fastapi_ok:
        print("✓ All database connections successful!")
        return 0
    else:
        print("✗ Some connections failed. Check your .env file and database setup.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

