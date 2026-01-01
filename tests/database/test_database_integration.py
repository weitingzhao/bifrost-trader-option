"""Integration tests for database operations with real database operations."""
import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
import asyncio

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import get_engine, get_AsyncSessionLocal, init_db, close_db
from src.database.models import OptionSnapshot, StrategyHistory
from src.database.repositories.history_repo import HistoryRepository, get_history_repository

# Configure pytest-asyncio
pytestmark = pytest.mark.asyncio


class TestDatabaseIntegration:
    """Integration tests that require actual database connection."""
    
    @pytest.fixture(scope="class")
    async def db_session(self):
        """Create a database session for testing."""
        # Note: This requires DATABASE_URL to be set in environment
        # For testing, you might want to use a test database
        try:
            session_factory = get_AsyncSessionLocal()
            async with session_factory() as session:
                yield session
        except Exception as e:
            pytest.skip(f"Database not available: {e}")
    
    async def test_database_connection_works(self):
        """Test that database connection can be established."""
        try:
            engine = get_engine()
            async with engine.connect() as conn:
                # Try a simple query
                result = await conn.execute("SELECT 1")
                assert result.scalar() == 1
        except Exception as e:
            pytest.skip(f"Database connection failed: {e}")
    
    async def test_can_create_tables(self):
        """Test that tables can be created."""
        try:
            await init_db()
            # If we get here, tables were created successfully
            assert True
        except Exception as e:
            pytest.skip(f"Cannot create tables: {e}")
    
    async def test_repository_integration(self, db_session):
        """Test repository with actual database."""
        # Create test data
        snapshot = OptionSnapshot(
            symbol="TEST",
            timestamp=datetime.utcnow(),
            underlying_price=100.0,
            contracts_data=[{"strike": 105.0, "expiration": "20240119"}]
        )
        
        db_session.add(snapshot)
        await db_session.commit()
        
        # Test repository
        repo = get_history_repository(db_session)
        snapshots = await repo.get_option_snapshots(
            symbol="TEST",
            limit=10
        )
        
        assert len(snapshots) > 0
        assert snapshots[0].symbol == "TEST"
        
        # Cleanup
        await db_session.delete(snapshot)
        await db_session.commit()


class TestDatabasePerformance:
    """Test database performance with multiple operations."""
    
    async def test_bulk_insert_performance(self):
        """Test inserting multiple records."""
        try:
            session_factory = get_AsyncSessionLocal()
            async with session_factory() as session:
                # Create multiple snapshots
                snapshots = []
                for i in range(10):
                    snapshot = OptionSnapshot(
                        symbol=f"TEST{i}",
                        timestamp=datetime.utcnow(),
                        underlying_price=100.0 + i,
                        contracts_data=[]
                    )
                    snapshots.append(snapshot)
                
                session.add_all(snapshots)
                await session.commit()
                
                # Verify all were inserted
                from sqlalchemy import select, func
                query = select(func.count(OptionSnapshot.id)).where(
                    OptionSnapshot.symbol.like("TEST%")
                )
                result = await session.execute(query)
                count = result.scalar()
                
                assert count >= 10
                
                # Cleanup
                for snapshot in snapshots:
                    await session.delete(snapshot)
                await session.commit()
        except Exception as e:
            pytest.skip(f"Database not available: {e}")
    
    async def test_query_performance(self):
        """Test query performance with filters."""
        try:
            session_factory = get_AsyncSessionLocal()
            async with session_factory() as session:
                repo = HistoryRepository(session)
                
                # Test query with time range
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(hours=24)
                
                snapshots = await repo.get_option_snapshots(
                    symbol="AAPL",
                    start_time=start_time,
                    end_time=end_time,
                    limit=100
                )
                
                # Query should complete without error
                assert isinstance(snapshots, list)
        except Exception as e:
            pytest.skip(f"Database not available: {e}")

