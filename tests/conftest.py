"""Pytest configuration and shared fixtures."""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure pytest-asyncio - this ensures async tests work
try:
    import pytest_asyncio
    # Mark all async test classes and functions automatically
    pytest_asyncio.plugin
except ImportError:
    pass  # pytest-asyncio will be installed when running tests

