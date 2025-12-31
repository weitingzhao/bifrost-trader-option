#!/usr/bin/env python3
"""
Python script to commit and push changes - bypasses Cursor shell issues
Uses subprocess to run git commands directly without shell initialization
"""
import subprocess
import sys
import os
from pathlib import Path

# Change to project directory
project_dir = Path(__file__).parent
os.chdir(project_dir)

def run_git_command(args, description):
    """Run a git command and handle errors."""
    print(f"📋 {description}...")
    try:
        result = subprocess.run(
            ['/usr/bin/git'] + args,
            capture_output=True,
            text=True,
            check=True,
            cwd=project_dir
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        sys.exit(1)

def main():
    print("🚀 Starting git commit and push process...\n")
    
    # Check status
    run_git_command(['status', '--short'], "Checking git status")
    
    # Stage all changes
    print("\n📦 Staging all changes...")
    run_git_command(['add', '-A'], "Staging changes")
    
    # Commit
    print("\n📝 Committing changes...")
    commit_message = """Refactor Streamlit monitoring app and add API development guide

- Created utils.py to consolidate shared functions (run_ssh_command, get_status, etc.)
- Removed duplicate code from app.py (~280 lines removed)
- Updated pages to import from utils.py for better maintainability
- Renamed 'FastAPI Live Logs' to 'API Logs' and made it child of 'APP-Server Status'
- Added comprehensive API development guide (docs/api/API_DEVELOPMENT_GUIDE.md)
- Added API changelog template (docs/api/API_CHANGELOG.md)
- Created API tracking script (scripts/track_api_changes.py)
- Improved code organization and maintainability"""
    
    run_git_command(['commit', '-m', commit_message], "Committing")
    
    # Get current branch
    print("\n🌿 Checking current branch...")
    branch_result = run_git_command(['branch', '--show-current'], "Getting branch name")
    branch = branch_result.stdout.strip()
    print(f"Current branch: {branch}")
    
    # Push
    print(f"\n🚀 Pushing to GitHub (origin/{branch})...")
    run_git_command(['push', 'origin', branch], "Pushing to GitHub")
    
    print("\n✅ Successfully pushed to GitHub!")

if __name__ == '__main__':
    main()

