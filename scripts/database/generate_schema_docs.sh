#!/bin/bash
# Generate markdown documentation from schema_all.sql
# Creates a readable schema documentation for MkDocs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "Generating Schema Documentation"
echo "=========================================="
echo ""

# Run Python script
python3 "$SCRIPT_DIR/generate_schema_docs.py"
import re
import sys

schema_file = sys.argv[1]

with open(schema_file, 'r') as f:
    content = f.read()

# Write header
print("# Complete Database Schema")
print()
print("This document provides a human-readable view of the complete database schema.")
print()
print("> **Note:** This is an auto-generated file. The source of truth is Django models (`app_django/apps/*/models.py`).")
print("> ")
print("> For the raw SQL schema, see: [schema_all.sql](schema_all.sql)")
print()
print("## Schema Overview")
print()
print("The database schema is organized into three Django apps:")
print()
print("- **Options App**: Stock symbols, option snapshots, and option contracts")
print("- **Strategies App**: Strategy history and market conditions")
print("- **Data Collection App**: Collection job tracking")
print()
print("---")
print()

# Find all CREATE TABLE statements with better regex
table_pattern = r'-- =+.*?TABLE: (\w+).*?Description: ([^\n]+).*?Django Model: ([^\n]+).*?CREATE TABLE IF NOT EXISTS (\w+)\s*\((.*?)\);'
matches = re.finditer(table_pattern, content, re.DOTALL | re.IGNORECASE)

tables = []
for match in matches:
    table_name = match.group(4)
    description = match.group(2).strip()
    django_model = match.group(3).strip()
    table_def = match.group(5)
    
    # Extract columns
    columns = []
    lines = table_def.split('\n')
    current_col = None
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('--'):
            continue
        
        # Check if line contains column definition
        # Match: column_name TYPE constraints,
        col_match = re.match(r'^(\w+)\s+([^,]+?)(?:,|$)', line)
        if col_match:
            col_name = col_match.group(1)
            col_def = col_match.group(2).strip()
            
            # Extract type
            type_match = re.match(r'([A-Z_]+(?:\s+[A-Z_]+)?)', col_def)
            col_type = type_match.group(1) if type_match else col_def.split()[0] if col_def.split() else 'UNKNOWN'
            
            # Determine constraints
            constraints = []
            if 'NOT NULL' in col_def.upper():
                constraints.append('NOT NULL')
            if 'UNIQUE' in col_def.upper():
                constraints.append('UNIQUE')
            if 'PRIMARY KEY' in col_def.upper():
                constraints.append('PRIMARY KEY')
            if 'DEFAULT' in col_def.upper():
                constraints.append('HAS DEFAULT')
            
            columns.append({
                'name': col_name,
                'type': col_type,
                'constraints': constraints,
                'full_def': col_def
            })
    
    tables.append({
        'name': table_name,
        'description': description,
        'django_model': django_model,
        'columns': columns
    })

# Write tables
for table in tables:
    print(f"## {table['name']}")
    print()
    print(f"**Description:** {table['description']}")
    print()
    print(f"**Django Model:** `{table['django_model']}`")
    print()
    print("### Columns")
    print()
    print("| Column Name | Type | Constraints | Description |")
    print("|------------|------|-------------|-------------|")
    
    for col in table['columns']:
        constraints_str = ', '.join(col['constraints']) if col['constraints'] else '-'
        
        # Add description based on column name
        desc = ""
        if col['name'].endswith('_id'):
            desc = "Foreign key reference"
        elif col['name'] == 'id':
            desc = "Primary key"
        elif col['name'] in ['created_at', 'updated_at', 'timestamp']:
            desc = "Timestamp"
        elif 'JSONB' in col['full_def'].upper() or 'JSON' in col['full_def'].upper():
            desc = "JSON data"
        elif col['name'] in ['symbol', 'name', 'sector', 'industry']:
            desc = "Text field"
        elif col['name'] in ['price', 'bid', 'ask', 'strike', 'underlying_price']:
            desc = "Price/numeric value"
        elif col['name'] in ['delta', 'gamma', 'theta', 'vega', 'implied_volatility']:
            desc = "Option Greek"
        elif col['name'] in ['volume', 'open_interest', 'records_collected']:
            desc = "Integer count"
        elif col['name'] in ['status', 'job_type', 'strategy_type', 'option_type']:
            desc = "Categorical value"
        else:
            desc = "-"
        
        print(f"| `{col['name']}` | `{col['type']}` | {constraints_str} | {desc} |")
    
    print()
    
    # Find indexes for this table
    index_pattern = rf"CREATE INDEX.*?ON {table['name']}\(([^)]+)\)"
    indexes = re.findall(index_pattern, content, re.IGNORECASE)
    if indexes:
        print("### Indexes")
        print()
        for idx in indexes:
            # Clean index definition
            idx_clean = idx.replace(',', ', ').strip()
            print(f"- `{idx_clean}`")
        print()
    
    # Find foreign keys
    fk_pattern = rf"REFERENCES (\w+)\((\w+)\)"
    fks = re.findall(fk_pattern, content)
    table_fks = []
    for fk_table, fk_col in fks:
        # Check if this FK is in the current table definition
        if fk_table in content[:content.find(f"CREATE TABLE IF NOT EXISTS {table['name']}") + 1000]:
            continue
        # Check if FK is mentioned in this table's section
        table_section_start = content.find(f"CREATE TABLE IF NOT EXISTS {table['name']}")
        if table_section_start != -1:
            table_section = content[table_section_start:table_section_start+2000]
            if f"REFERENCES {fk_table}" in table_section:
                table_fks.append((fk_table, fk_col))
    
    if table_fks:
        print("### Foreign Keys")
        print()
        for fk_table, fk_col in table_fks:
            print(f"- References `{fk_table}.{fk_col}`")
        print()
    
    print("---")
    print()

# Add footer
print()
print("## Related Files")
print()
print("- **Django Models**: `app_django/apps/*/models.py` (Single Source of Truth)")
print("- **SQLAlchemy Models**: `src/database/models.py`")
print("- **Raw SQL Schema**: [schema_all.sql](schema_all.sql)")
print("- **App-Specific Schemas**:")
print("  - [schema_options.sql](../../scripts/database/schema_options.sql)")
print("  - [schema_strategies.sql](../../scripts/database/schema_strategies.sql)")
print("  - [schema_data_collection.sql](../../scripts/database/schema_data_collection.sql)")
print()
print("## Regenerating This Documentation")
print()
print("This documentation is auto-generated from `schema_all.sql`. To regenerate:")
print()
print("```bash")
print("./scripts/database/combine_schemas.sh")
print("./scripts/database/generate_schema_docs.sh")
print("```")
print()
print("---")
print()
print("**Last Updated**: Auto-generated from schema files")

PYTHON_SCRIPT
"$SCHEMA_FILE"

echo ""
echo "✅ Schema documentation generated!"
echo "   Output: $DOCS_FILE"
echo ""
echo "📝 Next steps:"
echo "   1. Review the generated documentation"
echo "   2. Add to mkdocs.yml navigation if needed"
echo ""
