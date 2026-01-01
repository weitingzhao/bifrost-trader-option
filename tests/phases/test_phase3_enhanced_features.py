"""Tests for Phase 3: Enhanced Features tasks."""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestPlotlyCharts:
    """Test 3.1: Plotly Charts in Streamlit Analytics"""
    
    def test_plotly_in_requirements(self):
        """Verify Plotly is in requirements.txt."""
        requirements_file = project_root / 'requirements.txt'
        assert requirements_file.exists(), "requirements.txt not found"
        
        with open(requirements_file, 'r') as f:
            content = f.read()
            assert 'plotly' in content.lower(), "Plotly not found in requirements.txt"
    
    def test_analytics_pages_exist(self):
        """Verify analytics pages exist."""
        pages_dir = project_root / 'app_streamlit' / 'analytics' / 'pages'
        required_pages = [
            'strategy_performance.py',
            'option_chain_viewer.py',
            'profit_analysis.py',
        ]
        
        for page in required_pages:
            page_path = pages_dir / page
            assert page_path.exists(), f"Page {page} not found"


class TestHistoricalDataAPI:
    """Test 3.2: Historical Data API Endpoints"""
    
    def test_history_routes_exist(self):
        """Verify history routes module exists."""
        from src.api.routes import history
        assert history is not None
        assert hasattr(history, 'router')
    
    def test_history_endpoints_registered(self):
        """Verify history endpoints are registered."""
        from src.api.main import app
        routes = [r.path for r in app.routes if hasattr(r, 'path')]
        
        history_routes = [r for r in routes if 'history' in r]
        assert len(history_routes) > 0, "No history endpoints found"


class TestStreamlitAnalytics:
    """Test 3.3: Streamlit Analytics Dashboard"""
    
    def test_analytics_app_exists(self):
        """Verify analytics app exists."""
        analytics_app = project_root / 'app_streamlit' / 'analytics' / 'app.py'
        assert analytics_app.exists(), "Analytics app.py not found"
    
    def test_all_pages_exist(self):
        """Verify all analytics pages exist."""
        pages_dir = project_root / 'app_streamlit' / 'analytics' / 'pages'
        required_pages = [
            'strategy_performance.py',
            'option_chain_viewer.py',
            'profit_analysis.py',
            'backtesting.py',
        ]
        
        for page in required_pages:
            page_path = pages_dir / page
            assert page_path.exists(), f"Page {page} not found"


class TestVectorBTIntegration:
    """Test 3.4: VectorBT for Backtesting"""
    
    def test_vectorbt_in_requirements(self):
        """Verify VectorBT is in requirements.txt."""
        requirements_file = project_root / 'requirements.txt'
        assert requirements_file.exists(), "requirements.txt not found"
        
        with open(requirements_file, 'r') as f:
            content = f.read()
            assert 'vectorbt' in content.lower(), "VectorBT not found in requirements.txt"
    
    def test_backtesting_module_exists(self):
        """Verify backtesting module exists."""
        from src.backtesting import StrategyBacktester, BacktestResult
        assert StrategyBacktester is not None
        assert BacktestResult is not None
    
    def test_backtesting_routes_exist(self):
        """Verify backtesting routes exist."""
        from src.api.routes import backtesting
        assert backtesting is not None
        assert hasattr(backtesting, 'router')
    
    def test_backtesting_endpoints_registered(self):
        """Verify backtesting endpoints are registered."""
        from src.api.main import app
        routes = [r.path for r in app.routes if hasattr(r, 'path')]
        
        backtesting_routes = [r for r in routes if 'backtesting' in r]
        assert len(backtesting_routes) > 0, "No backtesting endpoints found"
    
    def test_vectorbt_engine_exists(self):
        """Verify VectorBT engine exists."""
        try:
            from src.backtesting.vectorbt_engine import VectorBTEngine
            assert VectorBTEngine is not None
        except ImportError:
            pytest.skip("VectorBT engine exists but VectorBT not installed (expected)")


class TestPricingUtilities:
    """Test 3.5: py_vollib for Advanced Pricing"""
    
    def test_py_vollib_in_requirements(self):
        """Verify py_vollib is in requirements.txt."""
        requirements_file = project_root / 'requirements.txt'
        assert requirements_file.exists(), "requirements.txt not found"
        
        with open(requirements_file, 'r') as f:
            content = f.read()
            assert 'py_vollib' in content.lower(), "py_vollib not found in requirements.txt"
    
    def test_pricing_utilities_exist(self):
        """Verify pricing utilities exist."""
        from src.utils.pricing import calculate_black_scholes_price
        assert callable(calculate_black_scholes_price)


class TestOptionChainVisualization:
    """Test 3.6: Option Chain Visualization"""
    
    def test_option_chain_viewer_exists(self):
        """Verify option chain viewer page exists."""
        viewer_page = project_root / 'app_streamlit' / 'analytics' / 'pages' / 'option_chain_viewer.py'
        assert viewer_page.exists(), "Option chain viewer page not found"
    
    def test_viewer_has_visualization_code(self):
        """Verify viewer has visualization code."""
        viewer_page = project_root / 'app_streamlit' / 'analytics' / 'pages' / 'option_chain_viewer.py'
        
        with open(viewer_page, 'r') as f:
            content = f.read().lower()
            # Check for common visualization keywords
            has_viz = any(keyword in content for keyword in ['plotly', 'chart', 'graph', 'figure'])
            assert has_viz, "Option chain viewer may not have visualization code"

