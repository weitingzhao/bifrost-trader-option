"""Tests for Phase 1: Foundation tasks."""
import pytest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestFastAPIStructure:
    """Test 1.1: FastAPI Basic Structure"""
    
    def test_fastapi_app_imports(self):
        """Verify FastAPI app can be imported."""
        from app_fastapi.api.main import app
        assert app is not None
        assert app.title == "Bifrost Options Trading Strategy Analyzer"
    
    def test_all_routes_registered(self):
        """Verify all expected routes are registered."""
        from app_fastapi.api.main import app
        routes = [r.path for r in app.routes if hasattr(r, 'path')]
        
        expected_routes = [
            '/api/health',
            '/api/stocks/{symbol}/options',
            '/api/strategies/analyze',
            '/api/backtesting/run',
        ]
        
        for route in expected_routes:
            # Check if route exists (accounting for path parameters)
            route_base = route.split('{')[0]
            assert any(route_base in r for r in routes), f"Route {route} not found"
    
    def test_health_endpoint_exists(self):
        """Verify health endpoint is accessible."""
        from app_fastapi.api.routes.health import router
        routes = [r.path for r in router.routes if hasattr(r, 'path')]
        assert '/api/health' in routes


class TestIBConnector:
    """Test 1.2: IB Connector Integration"""
    
    def test_ib_connector_module_exists(self):
        """Verify IB connector module exists."""
        from src.core.connector import ib
        assert ib is not None
    
    def test_connection_manager_exists(self):
        """Verify connection manager class exists."""
        from src.core.connector.ib import IBConnector
        assert IBConnector is not None
        assert hasattr(IBConnector, 'connect')
        assert hasattr(IBConnector, 'disconnect')


class TestStreamlitMonitoring:
    """Test 1.3: Streamlit Monitoring"""
    
    def test_monitoring_app_exists(self):
        """Verify monitoring app file exists."""
        monitoring_app = project_root / 'app_streamlit' / 'monitoring' / 'app.py'
        assert monitoring_app.exists(), "Monitoring app.py not found"
    
    def test_monitoring_app_imports(self):
        """Verify monitoring app can be imported."""
        import sys
        sys.path.insert(0, str(project_root / 'app_streamlit' / 'monitoring'))
        try:
            import app
            assert app is not None
        except Exception as e:
            pytest.skip(f"Monitoring app import failed (may need Streamlit): {e}")


class TestProjectStructure:
    """Test 1.4: Project Structure"""
    
    def test_required_directories_exist(self):
        """Verify all required directories exist."""
        required_dirs = [
            'app_fastapi/api',
            'app_fastapi/api/routes',
            'src/core',
            'src/analyzer',
            'src/database',
            'src/strategies',
            'src/utils',
            'src/backtesting',
        ]
        
        for dir_path in required_dirs:
            full_path = project_root / dir_path
            assert full_path.exists(), f"Directory {dir_path} not found"
            assert full_path.is_dir(), f"{dir_path} is not a directory"
    
    def test_key_files_exist(self):
        """Verify key files are in correct locations."""
        key_files = [
            'app_fastapi/api/main.py',
            'src/core/connector/ib.py',
            'src/core/options_chain.py',
            'src/analyzer/analyzer.py',
            'src/database/connection.py',
            'src/database/schemas.py',
            'src/database/models.py',
        ]
        
        for file_path in key_files:
            full_path = project_root / file_path
            assert full_path.exists(), f"File {file_path} not found"


class TestDjangoStructure:
    """Test 1.5: Django Project Structure"""
    
    def test_django_manage_exists(self):
        """Verify Django manage.py exists."""
        manage_py = project_root / 'app_django' / 'manage.py'
        assert manage_py.exists(), "Django manage.py not found"
    
    def test_django_config_exists(self):
        """Verify Django config directory exists."""
        config_dir = project_root / 'app_django' / 'django_config'
        assert config_dir.exists(), "Django config directory not found"
        assert (config_dir / 'settings.py').exists(), "Django settings.py not found"
    
    def test_app_djangos_exist(self):
        """Verify all required Django apps exist."""
        required_apps = ['options', 'strategies', 'data_collection']
        apps_dir = project_root / 'app_django' / 'apps'
        
        for app_name in required_apps:
            app_dir = apps_dir / app_name
            assert app_dir.exists(), f"Django app {app_name} not found"
            assert (app_dir / 'models.py').exists(), f"models.py not found for {app_name}"


class TestDatabaseConfiguration:
    """Test 1.6: Shared Database Configuration"""
    
    def test_sqlalchemy_connection_module(self):
        """Verify SQLAlchemy connection module exists."""
        from src.database.connection import get_engine, get_AsyncSessionLocal
        assert callable(get_engine)
        assert callable(get_AsyncSessionLocal)
    
    def test_sqlalchemy_models_exist(self):
        """Verify SQLAlchemy models exist."""
        from src.database.models import OptionSnapshot, StrategyHistory, Stock
        assert OptionSnapshot is not None
        assert StrategyHistory is not None
        assert Stock is not None
    
    def test_django_models_exist(self):
        """Verify Django models exist."""
        import sys
        sys.path.insert(0, str(project_root / 'app_django'))
        
        try:
            from apps.options.models import OptionSnapshot
            from apps.strategies.models import StrategyHistory
            assert OptionSnapshot is not None
            assert StrategyHistory is not None
        except Exception as e:
            pytest.skip(f"Django models import failed (may need Django setup): {e}")


class TestCelerySetup:
    """Test 1.7: Celery for Background Jobs"""
    
    def test_celery_app_exists(self):
        """Verify Celery app exists."""
        try:
            from services.celery_app import celery_app
            assert celery_app is not None
        except ImportError:
            pytest.skip("Celery not installed (expected in some environments)")
    
    def test_celery_tasks_exist(self):
        """Verify Celery tasks exist."""
        try:
            from services.tasks import collect_option_chain_data
            assert callable(collect_option_chain_data)
        except ImportError:
            pytest.skip("Celery not installed (expected in some environments)")
    
    def test_scheduler_exists(self):
        """Verify scheduler exists."""
        try:
            from services.scheduler import scheduler
            assert scheduler is not None
        except ImportError:
            pytest.skip("Celery not installed (expected in some environments)")

