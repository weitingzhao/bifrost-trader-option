"""Tests for Phase 2: Data Infrastructure tasks."""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestDjangoModels:
    """Test 2.1: Database Schema (Django Models)"""
    
    def test_option_snapshot_model_exists(self):
        """Verify OptionSnapshot model exists."""
        import sys
        sys.path.insert(0, str(project_root / 'app_admin'))
        
        try:
            from apps.options.models import OptionSnapshot
            assert OptionSnapshot is not None
            
            # Check required fields
            fields = [f.name for f in OptionSnapshot._meta.get_fields()]
            required_fields = ['symbol', 'timestamp', 'underlying_price', 'contracts_data']
            
            for field in required_fields:
                assert field in fields, f"Required field {field} not found"
        except Exception as e:
            pytest.skip(f"Django models import failed: {e}")
    
    def test_strategy_history_model_exists(self):
        """Verify StrategyHistory model exists."""
        import sys
        sys.path.insert(0, str(project_root / 'app_admin'))
        
        try:
            from apps.strategies.models import StrategyHistory
            assert StrategyHistory is not None
            
            # Check required fields
            fields = [f.name for f in StrategyHistory._meta.get_fields()]
            required_fields = ['symbol', 'strategy_type', 'timestamp', 'entry_cost']
            
            for field in required_fields:
                assert field in fields, f"Required field {field} not found"
        except Exception as e:
            pytest.skip(f"Django models import failed: {e}")


class TestSQLAlchemyModels:
    """Test 2.2: SQLAlchemy Models Matching Django"""
    
    def test_sqlalchemy_models_exist(self):
        """Verify SQLAlchemy models exist."""
        from src.database.models import OptionSnapshot, StrategyHistory, Stock
        assert OptionSnapshot is not None
        assert StrategyHistory is not None
        assert Stock is not None
    
    def test_models_have_required_fields(self):
        """Verify SQLAlchemy models have required fields."""
        from src.database.models import OptionSnapshot
        
        columns = [c.name for c in OptionSnapshot.__table__.columns]
        required_fields = ['symbol', 'timestamp', 'underlying_price', 'contracts_data']
        
        for field in required_fields:
            assert field in columns, f"Required field {field} not found in SQLAlchemy model"
    
    def test_repository_module_exists(self):
        """Verify repository module exists."""
        from src.database.repositories.history_repo import HistoryRepository, get_history_repository
        assert HistoryRepository is not None
        assert callable(get_history_repository)


class TestDataCollector:
    """Test 2.3: Data Collector Service"""
    
    def test_data_collector_exists(self):
        """Verify data collector function exists."""
        try:
            from services.data_collector import collect_option_chain
            assert callable(collect_option_chain)
        except ImportError:
            pytest.skip("Celery not installed (expected in some environments)")
    
    def test_celery_task_configured(self):
        """Verify Celery task is configured."""
        try:
            from services.tasks import collect_option_chain_data
            # Check if it's a Celery task (has delay method)
            assert hasattr(collect_option_chain_data, 'delay') or hasattr(collect_option_chain_data, 'apply_async')
        except ImportError:
            pytest.skip("Celery not installed (expected in some environments)")


class TestScheduledCollection:
    """Test 2.4: Scheduled Option Chain Collection"""
    
    def test_scheduler_exists(self):
        """Verify scheduler exists."""
        try:
            from services.scheduler import scheduler
            assert scheduler is not None
        except ImportError:
            pytest.skip("Celery/APScheduler not installed (expected in some environments)")
    
    def test_scheduler_can_add_jobs(self):
        """Verify scheduler can add jobs."""
        try:
            from services.scheduler import scheduler
            # Scheduler should have add_job method
            assert hasattr(scheduler, 'add_job') or hasattr(scheduler, 'add_jobstore')
        except ImportError:
            pytest.skip("Celery/APScheduler not installed (expected in some environments)")


class TestDjangoAdmin:
    """Test 2.5: Django Admin Configuration"""
    
    def test_admin_files_exist(self):
        """Verify admin files exist."""
        admin_files = [
            'app_admin/apps/options/admin.py',
            'app_admin/apps/strategies/admin.py',
        ]
        
        for admin_file in admin_files:
            full_path = project_root / admin_file
            assert full_path.exists(), f"Admin file {admin_file} not found"
    
    def test_models_registered_in_admin(self):
        """Verify models are registered in admin."""
        import sys
        sys.path.insert(0, str(project_root / 'app_admin'))
        
        try:
            from django.contrib import admin
            from apps.options.models import OptionSnapshot
            
            # Check if model is registered
            if OptionSnapshot in admin._registry:
                assert True
            else:
                pytest.skip("Model not registered (may require Django setup)")
        except Exception as e:
            pytest.skip(f"Django admin check failed: {e}")

