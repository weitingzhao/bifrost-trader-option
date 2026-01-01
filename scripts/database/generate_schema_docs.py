#!/usr/bin/env python3
"""
Generate markdown documentation from schema_all.sql
Creates a readable schema documentation for MkDocs
"""

import re
import sys
from pathlib import Path

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
        f.write("2. Generate this markdown documentation\n\n")
        f.write("---\n\n")
        f.write("**Last Updated**: Auto-generated from schema files\n")

def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    schema_file = script_dir / 'schema_all.sql'
    docs_file = project_root / 'docs' / 'database' / 'SCHEMA.md'
    
    if not schema_file.exists():
        print(f"❌ Error: schema_all.sql not found at {schema_file}")
        print("   Run ./scripts/database/refresh_schema.sh first")
        sys.exit(1)
    
    print("📄 Reading schema_all.sql...")
    tables = parse_schema_file(schema_file)
    
    print("📝 Generating markdown documentation...")
    generate_markdown(tables, docs_file)
    
    print(f"✅ Schema documentation generated!")
    print(f"   Output: {docs_file}")
    print(f"   Tables documented: {len(tables)}")
    print()

if __name__ == '__main__':
    main()

