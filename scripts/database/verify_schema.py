#!/usr/bin/env python3
"""
Verify that Django models, SQLAlchemy models, and schema.sql are in sync.

This script compares:
1. Django models (app_django/apps/*/models.py) - SINGLE SOURCE OF TRUTH
2. SQLAlchemy models (src/database/models.py)
3. Schema SQL (scripts/database/schema.sql)

Usage:
    ./scripts/database/verify_schema.py
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
# Add app_django to path for Django imports
sys.path.insert(0, str(project_root / 'app_django'))

# Color output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def get_django_tables() -> Dict[str, Dict]:
    """Extract table information from Django models."""
    tables = {}
    
    try:
        # Import Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_config.settings')
        import django
        django.setup()
        
        from django.apps import apps
        
        # Get all models (exclude Django system apps)
        django_system_apps = {'admin', 'auth', 'contenttypes', 'sessions'}
        
        for app_config in apps.get_app_configs():
            # Skip Django system apps
            if app_config.name in django_system_apps:
                continue
                
            for model in app_config.get_models():
                db_table = model._meta.db_table
                fields = {}
                
                # Extract field information (only actual database columns, not relationships)
                for field in model._meta.get_fields():
                    # Skip reverse relations and many-to-many relations
                    if field.many_to_many or (hasattr(field, 'related_model') and not hasattr(field, 'db_column')):
                        continue
                    
                    # Get the actual database column name
                    if hasattr(field, 'db_column'):
                        field_name = field.db_column or field.name
                    elif hasattr(field, 'column'):
                        field_name = field.column
                    else:
                        field_name = field.name
                    
                    # Skip relationship fields (they use _id suffix in database)
                    if hasattr(field, 'related_model'):
                        # ForeignKey fields have _id in database, but we want the actual column
                        if hasattr(field, 'attname'):
                            field_name = field.attname  # This gives us stock_id instead of stock
                        else:
                            continue
                    
                    field_type = type(field).__name__
                    fields[field_name] = {
                        'type': field_type,
                        'null': getattr(field, 'null', False),
                        'blank': getattr(field, 'blank', False),
                        'unique': getattr(field, 'unique', False),
                    }
                
                # Extract indexes
                indexes = []
                if hasattr(model._meta, 'indexes'):
                    for index in model._meta.indexes:
                        if hasattr(index, 'fields'):
                            index_fields = [f if isinstance(f, str) else f.name for f in index.fields]
                            indexes.append({
                                'name': getattr(index, 'name', None),
                                'fields': index_fields
                            })
                
                tables[db_table] = {
                    'fields': fields,
                    'indexes': indexes,
                    'app': app_config.name,
                    'model': model.__name__
                }
        
        return tables
    
    except Exception as e:
        print(f"{YELLOW}⚠️  Warning: Could not load Django models: {e}{NC}")
        print(f"{YELLOW}   Make sure Django is set up and models are accessible{NC}")
        return {}


def get_sqlalchemy_tables() -> Dict[str, Dict]:
    """Extract table information from SQLAlchemy models."""
    tables = {}
    
    try:
        from src.database.models import Base
        from sqlalchemy import inspect
        
        # Get all tables from Base metadata
        for table_name, table in Base.metadata.tables.items():
            fields = {}
            
            # Extract column information
            for column in table.columns:
                fields[column.name] = {
                    'type': str(column.type),
                    'nullable': column.nullable,
                    'unique': column.unique,
                    'primary_key': column.primary_key,
                }
            
            # Extract indexes
            indexes = []
            for index in table.indexes:
                indexes.append({
                    'name': index.name,
                    'columns': [col.name for col in index.columns]
                })
            
            tables[table_name] = {
                'fields': fields,
                'indexes': indexes
            }
        
        return tables
    
    except Exception as e:
        print(f"{YELLOW}⚠️  Warning: Could not load SQLAlchemy models: {e}{NC}")
        return {}


def get_schema_sql_tables() -> Dict[str, Set[str]]:
    """Extract table names from schema files."""
    schema_dir = project_root / 'scripts' / 'database'
    
    # Try schema_all.sql first (combined file), then fall back to individual files
    schema_files = [
        schema_dir / 'schema_all.sql',  # Combined file (preferred)
        schema_dir / 'schema_options.sql',  # Options app
        schema_dir / 'schema_strategies.sql',  # Strategies app
        schema_dir / 'schema_data_collection.sql',  # Data collection app
    ]
    
    tables = {}
    found_files = []
    
    for schema_file in schema_files:
        if schema_file.exists():
            found_files.append(schema_file.name)
            try:
                with open(schema_file, 'r') as f:
                    content = f.read()
                
                # Simple extraction of table names from CREATE TABLE statements
                import re
                table_pattern = r'CREATE TABLE IF NOT EXISTS (\w+)'
                matches = re.findall(table_pattern, content, re.IGNORECASE)
                
                for table_name in matches:
                    tables[table_name] = set()  # Placeholder for now
                
            except Exception as e:
                print(f"{YELLOW}⚠️  Warning: Could not parse {schema_file.name}: {e}{NC}")
    
    if not found_files:
        print(f"{YELLOW}⚠️  Warning: No schema files found in {schema_dir}{NC}")
        print(f"{YELLOW}   Looking for: schema_all.sql or schema_*.sql files{NC}")
        return {}
    
    if found_files:
        print(f"   Found tables in: {', '.join(found_files)}")
    
    return tables


def compare_tables(django_tables: Dict, sqlalchemy_tables: Dict, schema_tables: Dict) -> Tuple[bool, List[str]]:
    """Compare tables across all three sources."""
    issues = []
    
    # Django system tables that we don't need to track in SQLAlchemy or schema.sql
    django_system_tables = {
        'django_migrations', 'django_content_type', 'django_session', 
        'django_admin_log', 'auth_user', 'auth_group', 'auth_permission',
        'auth_user_groups', 'auth_user_user_permissions', 'auth_group_permissions'
    }
    
    # Filter out Django system tables from comparison
    django_app_tables = {k: v for k, v in django_tables.items() if k not in django_system_tables}
    sqlalchemy_app_tables = {k: v for k, v in sqlalchemy_tables.items() if k not in django_system_tables}
    schema_app_tables = {k: v for k, v in schema_tables.items() if k not in django_system_tables}
    
    all_table_names = set(django_app_tables.keys()) | set(sqlalchemy_app_tables.keys()) | set(schema_app_tables.keys())
    
    # Check if all tables exist in all three
    for table_name in all_table_names:
        in_django = table_name in django_tables
        in_sqlalchemy = table_name in sqlalchemy_tables
        in_schema = table_name in schema_tables
        
        if not in_django:
            issues.append(f"❌ Table '{table_name}' missing in Django models (SINGLE SOURCE OF TRUTH)")
        if not in_sqlalchemy:
            issues.append(f"❌ Table '{table_name}' missing in SQLAlchemy models")
        if not in_schema:
            issues.append(f"⚠️  Table '{table_name}' missing in schema files")
    
    # Compare fields for tables that exist in both Django and SQLAlchemy
    for table_name in django_app_tables.keys():
        if table_name in sqlalchemy_app_tables:
            django_fields = set(django_app_tables[table_name]['fields'].keys())
            sqlalchemy_fields = set(sqlalchemy_app_tables[table_name]['fields'].keys())
            
            # Normalize field names (handle relationship vs column name differences)
            # Django might have 'stock' but SQLAlchemy has 'stock_id'
            normalized_django_fields = set()
            for field in django_fields:
                # If it's a relationship field, check for _id version
                if field.endswith('_id'):
                    normalized_django_fields.add(field)
                else:
                    # Check if there's a corresponding _id field
                    if f"{field}_id" in sqlalchemy_fields:
                        normalized_django_fields.add(f"{field}_id")
                    else:
                        normalized_django_fields.add(field)
            
            missing_in_sqlalchemy = normalized_django_fields - sqlalchemy_fields
            missing_in_django = sqlalchemy_fields - normalized_django_fields
            
            # Filter out common Django system fields that might not be in SQLAlchemy
            django_system_fields = {'id'}  # id is usually auto-generated
            missing_in_sqlalchemy = missing_in_sqlalchemy - django_system_fields
            
            if missing_in_sqlalchemy:
                issues.append(f"❌ Table '{table_name}': Fields missing in SQLAlchemy: {missing_in_sqlalchemy}")
            if missing_in_django and table_name not in ['django_migrations']:  # Ignore migrations table
                # Only warn about extra fields if they're significant
                significant_extra = missing_in_django - {'id'}  # id is usually fine
                if significant_extra:
                    issues.append(f"⚠️  Table '{table_name}': Extra fields in SQLAlchemy: {significant_extra}")
    
    return len(issues) == 0, issues


def main():
    """Main verification function."""
    print("=" * 60)
    print(f"{BLUE}Database Schema Verification{NC}")
    print("=" * 60)
    print()
    print(f"{BLUE}Single Source of Truth: Django Models{NC}")
    print(f"{BLUE}Comparing: Django → SQLAlchemy → schema.sql{NC}")
    print()
    
    # Load all three sources
    print(f"{BLUE}Loading Django models...{NC}")
    django_tables = get_django_tables()
    print(f"   Found {len(django_tables)} tables in Django models")
    
    print(f"{BLUE}Loading SQLAlchemy models...{NC}")
    sqlalchemy_tables = get_sqlalchemy_tables()
    print(f"   Found {len(sqlalchemy_tables)} tables in SQLAlchemy models")
    
    print(f"{BLUE}Loading schema files...{NC}")
    schema_tables = get_schema_sql_tables()
    print(f"   Found {len(schema_tables)} tables in schema files")
    print()
    
    # Compare
    print("=" * 60)
    print(f"{BLUE}Comparing schemas...{NC}")
    print("=" * 60)
    print()
    
    is_sync, issues = compare_tables(django_tables, sqlalchemy_tables, schema_tables)
    
    if is_sync:
        print(f"{GREEN}✅ All schemas are in sync!{NC}")
        print()
        print(f"{GREEN}Summary:{NC}")
        # Count only app tables (exclude Django system tables)
        django_app_count = len([t for t in django_tables.keys() if t not in {
            'django_migrations', 'django_content_type', 'django_session', 
            'django_admin_log', 'auth_user', 'auth_group', 'auth_permission',
            'auth_user_groups', 'auth_user_user_permissions', 'auth_group_permissions'
        }])
        print(f"   - Django models: {django_app_count} app tables (plus {len(django_tables) - django_app_count} Django system tables)")
        print(f"   - SQLAlchemy models: {len(sqlalchemy_tables)} tables")
        print(f"   - Schema files: {len(schema_tables)} tables")
        return 0
    else:
        print(f"{RED}❌ Schema discrepancies found:{NC}")
        print()
        for issue in issues:
            print(f"   {issue}")
        print()
        print(f"{YELLOW}⚠️  Fix discrepancies by:{NC}")
        print(f"   1. Update Django models (if needed) - SINGLE SOURCE OF TRUTH")
        print(f"   2. Update SQLAlchemy models to match Django models")
        print(f"   3. Update schema files (schema_*.sql) to match Django models")
        print(f"   4. Regenerate schema files: ./scripts/database/refresh_schema.sh")
        print(f"   5. Run this script again to verify")
        return 1


if __name__ == '__main__':
    sys.exit(main())

