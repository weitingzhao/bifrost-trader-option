#!/usr/bin/env python3
"""
API Change Tracking Script
Tracks and compares API endpoint changes over time.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import argparse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from app_api.api.main import app


def export_openapi_schema(output_path: str = "api_schemas"):
    """Export current OpenAPI schema to file."""
    schema = app.openapi()
    
    # Create output directory
    output_dir = Path(output_path)
    output_dir.mkdir(exist_ok=True)
    
    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_dir / f"openapi_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(schema, f, indent=2)
    
    print(f"✅ Exported OpenAPI schema to: {filename}")
    return filename


def compare_schemas(old_schema_path: str, new_schema_path: str):
    """Compare two OpenAPI schemas and show differences."""
    try:
        from deepdiff import DeepDiff
    except ImportError:
        print("⚠️  deepdiff not installed. Install with: pip install deepdiff")
        return
    
    with open(old_schema_path) as f:
        old_schema = json.load(f)
    
    with open(new_schema_path) as f:
        new_schema = json.load(f)
    
    diff = DeepDiff(old_schema, new_schema, ignore_order=True, verbose_level=2)
    
    if not diff:
        print("✅ No changes detected")
        return
    
    print("\n📊 Schema Changes Detected:\n")
    
    # New endpoints
    if "dictionary_item_added" in diff:
        print("➕ New Endpoints:")
        for item in diff["dictionary_item_added"]:
            print(f"  - {item}")
    
    # Removed endpoints
    if "dictionary_item_removed" in diff:
        print("\n➖ Removed Endpoints:")
        for item in diff["dictionary_item_removed"]:
            print(f"  - {item}")
    
    # Modified endpoints
    if "values_changed" in diff:
        print("\n🔄 Modified Endpoints:")
        for change in diff["values_changed"]:
            print(f"  - {change}")
            print(f"    Old: {diff['values_changed'][change]['old_value']}")
            print(f"    New: {diff['values_changed'][change]['new_value']}")
    
    # Save diff to file
    diff_file = Path("api_schemas") / f"diff_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(diff_file, "w") as f:
        json.dump(diff, f, indent=2, default=str)
    
    print(f"\n📄 Full diff saved to: {diff_file}")


def list_endpoints():
    """List all current API endpoints with their models."""
    print("\n📋 Current API Endpoints:\n")
    
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            methods = ", ".join(route.methods)
            path = route.path
            
            # Get response model if available
            response_model = getattr(route, "response_model", None)
            response_info = f" → {response_model.__name__}" if response_model else ""
            
            print(f"  {methods:10} {path}{response_info}")


def generate_changelog(schema_path: str):
    """Generate changelog from OpenAPI schema."""
    with open(schema_path) as f:
        schema = json.load(f)
    
    changelog = {
        "version": schema.get("info", {}).get("version", "unknown"),
        "generated_at": datetime.now().isoformat(),
        "endpoints": []
    }
    
    paths = schema.get("paths", {})
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() in ["get", "post", "put", "delete", "patch"]:
                endpoint_info = {
                    "path": path,
                    "method": method.upper(),
                    "summary": details.get("summary", ""),
                    "description": details.get("description", ""),
                    "request_model": None,
                    "response_model": None
                }
                
                # Get request body schema
                if "requestBody" in details:
                    content = details["requestBody"].get("content", {})
                    if "application/json" in content:
                        ref = content["application/json"]["schema"].get("$ref", "")
                        if ref:
                            endpoint_info["request_model"] = ref.split("/")[-1]
                
                # Get response schema
                responses = details.get("responses", {})
                if "200" in responses:
                    content = responses["200"].get("content", {})
                    if "application/json" in content:
                        ref = content["application/json"]["schema"].get("$ref", "")
                        if ref:
                            endpoint_info["response_model"] = ref.split("/")[-1]
                
                changelog["endpoints"].append(endpoint_info)
    
    # Save changelog
    changelog_file = Path("api_schemas") / f"changelog_{datetime.now().strftime('%Y%m%d')}.json"
    with open(changelog_file, "w") as f:
        json.dump(changelog, f, indent=2)
    
    print(f"✅ Changelog generated: {changelog_file}")
    return changelog_file


def main():
    parser = argparse.ArgumentParser(description="Track API endpoint changes")
    parser.add_argument("action", choices=["export", "compare", "list", "changelog"],
                       help="Action to perform")
    parser.add_argument("--old", help="Path to old schema file (for compare)")
    parser.add_argument("--new", help="Path to new schema file (for compare)")
    
    args = parser.parse_args()
    
    if args.action == "export":
        export_openapi_schema()
    elif args.action == "compare":
        if not args.old or not args.new:
            print("❌ Error: --old and --new required for compare")
            sys.exit(1)
        compare_schemas(args.old, args.new)
    elif args.action == "list":
        list_endpoints()
    elif args.action == "changelog":
        if not args.new:
            # Export current schema first
            schema_file = export_openapi_schema()
            generate_changelog(str(schema_file))
        else:
            generate_changelog(args.new)


if __name__ == "__main__":
    main()

