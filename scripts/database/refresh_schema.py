#!/usr/bin/env python3
"""
Refresh database schema files and verify synchronization
Combines app-specific schema files, generates markdown documentation, and verifies sync

This script:
   1. Combines schema_*.sql files into schema_all.sql
   2. Generates markdown documentation (SCHEMA.md) for MkDocs
   3. Verifies that Django models, SQLAlchemy models, and schema files are in sync
"""

import re
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


# ============================================================================
# SCHEMA GENERATION FUNCTIONS
# ============================================================================

def parse_schema_file(schema_file: Path) -> dict:
    """Parse schema SQL file and extract table information."""
    with open(schema_file, 'r') as f:
        content = f.read()
    
    tables = {}
    current_table = None
    current_section = None
    
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for table header comment
        if 'TABLE:' in line and 'Description:' in line:
            table_match = re.search(r'TABLE:\s+(\w+)', line)
            desc_match = re.search(r'Description:\s+(.+)', line)
            if table_match:
                current_table = table_match.group(1)
                description = desc_match.group(1).strip() if desc_match else ""
                
                # Get Django model from next line
                django_model = ""
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if 'Django Model:' in next_line:
                        model_match = re.search(r'Django Model:\s+(.+)', next_line)
                        if model_match:
                            django_model = model_match.group(1).strip()
                
                tables[current_table] = {
                    'description': description,
                    'django_model': django_model,
                    'columns': [],
                    'indexes': [],
                    'foreign_keys': []
                }
        
        # Check for CREATE TABLE statement
        elif line.startswith('CREATE TABLE IF NOT EXISTS'):
            table_match = re.search(r'CREATE TABLE IF NOT EXISTS\s+(\w+)', line)
            if table_match:
                current_table = table_match.group(1)
                if current_table not in tables:
                    tables[current_table] = {
                        'description': f"{current_table} table",
                        'django_model': "",
                        'columns': [],
                        'indexes': [],
                        'foreign_keys': []
                    }
                current_section = 'columns'
                i += 1
                continue
        
        # Parse columns
        if current_table and current_section == 'columns':
            # Check if line is a column definition
            if re.match(r'^\w+\s+[A-Z_]', line) and not line.startswith('--'):
                # Extract column name and type
                col_match = re.match(r'^(\w+)\s+([^,]+?)(?:,|$)', line)
                if col_match:
                    col_name = col_match.group(1)
                    col_def = col_match.group(2).strip()
                    
                    # Extract type
                    type_parts = col_def.split()
                    col_type = type_parts[0] if type_parts else 'UNKNOWN'
                    if len(type_parts) > 1 and type_parts[1] in ['WITH', 'PRECISION']:
                        col_type = ' '.join(type_parts[:2])
                    
                    # Determine constraints
                    constraints = []
                    if 'NOT NULL' in col_def.upper():
                        constraints.append('NOT NULL')
                    if 'UNIQUE' in col_def.upper() and 'PRIMARY KEY' not in col_def.upper():
                        constraints.append('UNIQUE')
                    if 'PRIMARY KEY' in col_def.upper():
                        constraints.append('PRIMARY KEY')
                    if 'DEFAULT' in col_def.upper():
                        constraints.append('HAS DEFAULT')
                    
                    # Check for foreign key
                    fk_match = re.search(r'REFERENCES\s+(\w+)\((\w+)\)', col_def)
                    if fk_match:
                        tables[current_table]['foreign_keys'].append({
                            'column': col_name,
                            'references_table': fk_match.group(1),
                            'references_column': fk_match.group(2)
                        })
                    
                    tables[current_table]['columns'].append({
                        'name': col_name,
                        'type': col_type,
                        'constraints': constraints,
                        'full_def': col_def
                    })
            
            # Check if we've reached the end of CREATE TABLE
            if line == ');':
                current_section = None
        
        # Parse indexes
        if current_table and 'CREATE INDEX' in line:
            idx_match = re.search(r'CREATE INDEX.*?ON\s+' + re.escape(current_table) + r'\s*\(([^)]+)\)', line)
            if idx_match:
                idx_cols = idx_match.group(1).strip()
                tables[current_table]['indexes'].append(idx_cols)
        
        i += 1
    
    return tables

def generate_markdown(tables: dict, output_file: Path):
    """Generate markdown documentation from parsed tables."""
    with open(output_file, 'w') as f:
        # Header
        f.write("# Complete Database Schema\n\n")
        f.write("This document provides a human-readable view of the complete database schema.\n\n")
        f.write("> **Note:** This is an auto-generated file. The source of truth is Django models (`app_django/apps/*/models.py`).\n")
        f.write("> \n")
        f.write("> For the raw SQL schema, see: [schema_all.sql](schema_all.sql)\n\n")
        f.write("## Schema Overview\n\n")
        f.write("The database schema is organized into three Django apps:\n\n")
        f.write("- **Options App**: Stock symbols, option snapshots, and option contracts\n")
        f.write("- **Strategies App**: Strategy history and market conditions\n")
        f.write("- **Data Collection App**: Collection job tracking\n\n")
        f.write("---\n\n")
        
        # Write each table
        for table_name, table_info in sorted(tables.items()):
            f.write(f"## {table_name}\n\n")
            f.write(f"**Description:** {table_info['description']}\n\n")
            if table_info['django_model']:
                f.write(f"**Django Model:** `{table_info['django_model']}`\n\n")
            
            # Columns
            f.write("### Columns\n\n")
            f.write("| Column Name | Type | Constraints | Description |\n")
            f.write("|------------|------|-------------|-------------|\n")
            
            for col in table_info['columns']:
                constraints_str = ', '.join(col['constraints']) if col['constraints'] else '-'
                
                # Add description based on column name and type
                desc = ""
                if col['name'].endswith('_id') and col['name'] != 'id':
                    desc = "Foreign key reference"
                elif col['name'] == 'id':
                    desc = "Primary key"
                elif col['name'] in ['created_at', 'updated_at', 'timestamp', 'started_at', 'completed_at']:
                    desc = "Timestamp"
                elif 'JSONB' in col['full_def'].upper() or 'JSON' in col['full_def'].upper():
                    desc = "JSON data"
                elif col['name'] in ['symbol', 'name', 'sector', 'industry', 'error_message']:
                    desc = "Text field"
                elif col['name'] in ['price', 'bid', 'ask', 'strike', 'underlying_price', 'sp500_price', 'entry_cost', 'max_profit', 'max_loss']:
                    desc = "Price/numeric value"
                elif col['name'] in ['delta', 'gamma', 'theta', 'vega', 'implied_volatility', 'vix']:
                    desc = "Option Greek / Volatility"
                elif col['name'] in ['volume', 'open_interest', 'records_collected']:
                    desc = "Integer count"
                elif col['name'] in ['status', 'job_type', 'strategy_type', 'option_type', 'market_trend', 'volatility_regime']:
                    desc = "Categorical value"
                else:
                    desc = "-"
                
                f.write(f"| `{col['name']}` | `{col['type']}` | {constraints_str} | {desc} |\n")
            
            f.write("\n")
            
            # Foreign Keys
            if table_info['foreign_keys']:
                f.write("### Foreign Keys\n\n")
                for fk in table_info['foreign_keys']:
                    f.write(f"- `{fk['column']}` → `{fk['references_table']}.{fk['references_column']}`\n")
                f.write("\n")
            
            # Indexes
            if table_info['indexes']:
                f.write("### Indexes\n\n")
                for idx in table_info['indexes']:
                    f.write(f"- `{idx}`\n")
                f.write("\n")
            
            f.write("---\n\n")
        
        # Footer
        f.write("## Related Files\n\n")
        f.write("- **Django Models**: `app_django/apps/*/models.py` (Single Source of Truth)\n")
        f.write("- **SQLAlchemy Models**: `src/database/models.py`\n")
        f.write("- **Raw SQL Schema**: [schema_all.sql](schema_all.sql)\n")
        f.write("- **App-Specific Schemas**:\n")
        f.write("  - [schema_options.sql](../../scripts/database/schema_options.sql)\n")
        f.write("  - [schema_strategies.sql](../../scripts/database/schema_strategies.sql)\n")
        f.write("  - [schema_data_collection.sql](../../scripts/database/schema_data_collection.sql)\n\n")
        f.write("## Regenerating This Documentation\n\n")
        f.write("This documentation is auto-generated from `schema_all.sql`. To regenerate:\n\n")
        f.write("```bash\n")
        f.write("./scripts/database/refresh_schema.sh\n")
        f.write("```\n\n")
        f.write("This single command will:\n")
        f.write("1. Combine all app-specific schema files into `schema_all.sql`\n")
        f.write("2. Generate this markdown documentation\n")
        f.write("3. Verify schema synchronization\n\n")
        f.write("---\n\n")
        f.write("**Last Updated**: Auto-generated from schema files\n")


# ============================================================================
# SCHEMA VERIFICATION FUNCTIONS
# ============================================================================

def get_django_tables() -> Dict[str, Dict]:
    """Extract table information from Django models."""
    tables = {}
    
    try:
        # Try to import Django - if it fails, return empty dict
        try:
            import django
        except ImportError:
            return {}
        
        # Import Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_config.settings')
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
    
    # Django system tables that we don't need to track in SQLAlchemy or schema files
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
    django_available = len(django_tables) > 0
    
    for table_name in all_table_names:
        in_django = table_name in django_tables
        in_sqlalchemy = table_name in sqlalchemy_tables
        in_schema = table_name in schema_tables
        
        # Only check Django if it's available
        if django_available and not in_django:
            issues.append(f"❌ Table '{table_name}' missing in Django models (SINGLE SOURCE OF TRUTH)")
        if not in_sqlalchemy:
            issues.append(f"❌ Table '{table_name}' missing in SQLAlchemy models")
        if not in_schema:
            issues.append(f"⚠️  Table '{table_name}' missing in schema files")
    
    # Compare fields for tables that exist in both Django and SQLAlchemy (only if Django is available)
    if django_available:
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
    
    # If Django is not available, only verify SQLAlchemy vs schema files
    if not django_available:
        # Check SQLAlchemy vs schema files
        for table_name in sqlalchemy_app_tables.keys():
            if table_name not in schema_app_tables:
                issues.append(f"⚠️  Table '{table_name}' in SQLAlchemy but missing in schema files")
        for table_name in schema_app_tables.keys():
            if table_name not in sqlalchemy_app_tables:
                issues.append(f"⚠️  Table '{table_name}' in schema files but missing in SQLAlchemy")
    
    return len(issues) == 0, issues


def verify_schema() -> int:
    """Verify that Django models, SQLAlchemy models, and schema files are in sync."""
    print("=" * 60)
    print(f"{BLUE}Database Schema Verification{NC}")
    print("=" * 60)
    print()
    print(f"{BLUE}Single Source of Truth: Django Models{NC}")
    print(f"{BLUE}Comparing: Django → SQLAlchemy → schema files{NC}")
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
        django_available = len(django_tables) > 0
        if django_available:
            django_app_count = len([t for t in django_tables.keys() if t not in {
                'django_migrations', 'django_content_type', 'django_session', 
                'django_admin_log', 'auth_user', 'auth_group', 'auth_permission',
                'auth_user_groups', 'auth_user_user_permissions', 'auth_group_permissions'
            }])
            print(f"   - Django models: {django_app_count} app tables (plus {len(django_tables) - django_app_count} Django system tables)")
        else:
            print(f"   - Django models: Not available (Django not installed or not accessible)")
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
        print(f"   4. Run refresh_schema.sh again to regenerate and verify")
        return 1


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function - generates schema docs and optionally verifies sync."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Refresh database schema files and verify synchronization')
    parser.add_argument('--verify-only', action='store_true', 
                       help='Only verify schema sync, do not generate files')
    parser.add_argument('--no-verify', action='store_true',
                       help='Skip verification after generating files')
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    schema_file = script_dir / 'schema_all.sql'
    docs_file = project_root / 'docs' / 'database' / 'SCHEMA.md'
    
    # If verify-only, just run verification
    if args.verify_only:
        return verify_schema()
    
    # Generate schema documentation
    if not schema_file.exists():
        print(f"❌ Error: schema_all.sql not found at {schema_file}")
        print("   Run ./scripts/database/refresh_schema.sh first (it will generate schema_all.sql)")
        return 1
    
    print("📄 Reading schema_all.sql...")
    tables = parse_schema_file(schema_file)
    
    print("📝 Generating markdown documentation...")
    generate_markdown(tables, docs_file)
    
    print(f"✅ Schema documentation generated!")
    print(f"   Output: {docs_file}")
    print(f"   Tables documented: {len(tables)}")
    print()
    
    # Run verification unless --no-verify is specified
    if not args.no_verify:
        print()
        return verify_schema()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
