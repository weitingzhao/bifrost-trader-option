"""Database integration tests for actual database operations."""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.models import OptionSnapshot, StrategyHistory, Stock, Base
from src.database.repositories.history_repo import HistoryRepository

# Configure pytest-asyncio
pytestmark = pytest.mark.asyncio

# Test database URL (using in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


class TestDatabaseConnection:
    """Test database connection and basic operations."""

    async def test_database_connection(self, test_engine):
        """Test that we can connect to the database."""
        async with test_engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            assert result.scalar() == 1

    async def test_tables_created(self, test_engine):
        """Test that all tables are created."""
        from sqlalchemy import text, inspect

        async with test_engine.connect() as conn:
            # For SQLite, we can check table names
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = [row[0] for row in result]
            # Check for table names (SQLAlchemy may use different naming)
            table_names_lower = [t.lower() for t in tables]
            assert any(
                "option" in t and "snapshot" in t for t in table_names_lower
            ) or any("optionsnapshot" in t for t in table_names_lower)
            assert any(
                "strategy" in t and "history" in t for t in table_names_lower
            ) or any("strategyhistory" in t for t in table_names_lower)


class TestOptionSnapshotOperations:
    """Test OptionSnapshot CRUD operations."""

    async def test_create_option_snapshot(self, test_session):
        """Test creating an option snapshot."""
        snapshot = OptionSnapshot(
            symbol="AAPL",
            timestamp=datetime.utcnow(),
            underlying_price=150.0,
            contracts_data=[
                {
                    "strike": 155.0,
                    "expiration": "20240119",
                    "option_type": "CALL",
                    "bid": 2.50,
                    "ask": 2.60,
                }
            ],
        )

        test_session.add(snapshot)
        await test_session.commit()
        await test_session.refresh(snapshot)

        assert snapshot.id is not None
        assert snapshot.symbol == "AAPL"
        assert snapshot.underlying_price == 150.0

    async def test_query_option_snapshots(self, test_session):
        """Test querying option snapshots."""
        # Create test data
        snapshot1 = OptionSnapshot(
            symbol="AAPL",
            timestamp=datetime.utcnow(),
            underlying_price=150.0,
            contracts_data=[],
        )
        snapshot2 = OptionSnapshot(
            symbol="MSFT",
            timestamp=datetime.utcnow(),
            underlying_price=300.0,
            contracts_data=[],
        )

        test_session.add(snapshot1)
        test_session.add(snapshot2)
        await test_session.commit()

        # Query by symbol
        from sqlalchemy import select

        query = select(OptionSnapshot).where(OptionSnapshot.symbol == "AAPL")
        result = await test_session.execute(query)
        snapshots = result.scalars().all()

        assert len(snapshots) == 1
        assert snapshots[0].symbol == "AAPL"

    async def test_update_option_snapshot(self, test_session):
        """Test updating an option snapshot."""
        snapshot = OptionSnapshot(
            symbol="AAPL",
            timestamp=datetime.utcnow(),
            underlying_price=150.0,
            contracts_data=[],
        )

        test_session.add(snapshot)
        await test_session.commit()
        await test_session.refresh(snapshot)

        # Update
        snapshot.underlying_price = 155.0
        await test_session.commit()
        await test_session.refresh(snapshot)

        assert snapshot.underlying_price == 155.0

    async def test_delete_option_snapshot(self, test_session):
        """Test deleting an option snapshot."""
        snapshot = OptionSnapshot(
            symbol="AAPL",
            timestamp=datetime.utcnow(),
            underlying_price=150.0,
            contracts_data=[],
        )

        test_session.add(snapshot)
        await test_session.commit()
        await test_session.refresh(snapshot)

        snapshot_id = snapshot.id

        # Delete
        await test_session.delete(snapshot)
        await test_session.commit()

        # Verify deleted
        from sqlalchemy import select

        query = select(OptionSnapshot).where(OptionSnapshot.id == snapshot_id)
        result = await test_session.execute(query)
        assert result.scalar_one_or_none() is None


class TestStrategyHistoryOperations:
    """Test StrategyHistory CRUD operations."""

    async def test_create_strategy_history(self, test_session):
        """Test creating a strategy history record."""
        history = StrategyHistory(
            symbol="AAPL",
            strategy_type="covered_call",
            timestamp=datetime.utcnow(),
            entry_cost=-15000.0,
            max_profit=500.0,
            max_loss=15000.0,
            risk_reward_ratio=0.033,
        )

        test_session.add(history)
        await test_session.commit()
        await test_session.refresh(history)

        assert history.id is not None
        assert history.symbol == "AAPL"
        assert history.strategy_type == "covered_call"
        assert history.entry_cost == -15000.0

    async def test_query_strategy_history(self, test_session):
        """Test querying strategy history."""
        # Create test data
        history1 = StrategyHistory(
            symbol="AAPL",
            strategy_type="covered_call",
            timestamp=datetime.utcnow(),
            entry_cost=-15000.0,
            max_profit=500.0,
            max_loss=15000.0,
        )
        history2 = StrategyHistory(
            symbol="MSFT",
            strategy_type="iron_condor",
            timestamp=datetime.utcnow(),
            entry_cost=-200.0,
            max_profit=300.0,
            max_loss=200.0,
        )

        test_session.add(history1)
        test_session.add(history2)
        await test_session.commit()

        # Query by symbol
        from sqlalchemy import select

        query = select(StrategyHistory).where(StrategyHistory.symbol == "AAPL")
        result = await test_session.execute(query)
        histories = result.scalars().all()

        assert len(histories) == 1
        assert histories[0].symbol == "AAPL"
        assert histories[0].strategy_type == "covered_call"


class TestHistoryRepository:
    """Test HistoryRepository database operations."""

    async def test_repository_get_option_snapshots(self, test_session):
        """Test repository get_option_snapshots method."""
        # Create test data
        now = datetime.utcnow()
        snapshot1 = OptionSnapshot(
            symbol="AAPL", timestamp=now, underlying_price=150.0, contracts_data=[]
        )
        snapshot2 = OptionSnapshot(
            symbol="AAPL", timestamp=now, underlying_price=151.0, contracts_data=[]
        )
        snapshot3 = OptionSnapshot(
            symbol="MSFT", timestamp=now, underlying_price=300.0, contracts_data=[]
        )

        test_session.add(snapshot1)
        test_session.add(snapshot2)
        test_session.add(snapshot3)
        await test_session.commit()

        # Test repository
        repo = HistoryRepository(test_session)
        snapshots = await repo.get_option_snapshots(
            symbol="AAPL", start_time=now, end_time=now, limit=10
        )

        assert len(snapshots) == 2
        assert all(s.symbol == "AAPL" for s in snapshots)

    async def test_repository_get_strategy_history(self, test_session):
        """Test repository get_strategy_history method."""
        # Create test data
        now = datetime.utcnow()
        history1 = StrategyHistory(
            symbol="AAPL",
            strategy_type="covered_call",
            timestamp=now,
            entry_cost=-15000.0,
            max_profit=500.0,
            max_loss=15000.0,
        )
        history2 = StrategyHistory(
            symbol="AAPL",
            strategy_type="iron_condor",
            timestamp=now,
            entry_cost=-200.0,
            max_profit=300.0,
            max_loss=200.0,
        )

        test_session.add(history1)
        test_session.add(history2)
        await test_session.commit()

        # Test repository
        repo = HistoryRepository(test_session)
        histories = await repo.get_strategy_history(
            symbol="AAPL", start_time=now, end_time=now, limit=10
        )

        assert len(histories) == 2
        assert all(h.symbol == "AAPL" for h in histories)

        # Test filtering by strategy_type
        histories = await repo.get_strategy_history(
            symbol="AAPL",
            strategy_type="covered_call",
            start_time=now,
            end_time=now,
            limit=10,
        )

        assert len(histories) == 1
        assert histories[0].strategy_type == "covered_call"


class TestDatabaseTransactions:
    """Test database transaction handling."""

    async def test_transaction_rollback(self, test_session):
        """Test that transactions can be rolled back."""
        snapshot = OptionSnapshot(
            symbol="AAPL",
            timestamp=datetime.utcnow(),
            underlying_price=150.0,
            contracts_data=[],
        )

        test_session.add(snapshot)
        await test_session.flush()  # Flush but don't commit

        # Verify it exists before rollback
        snapshot_id = snapshot.id
        assert snapshot_id is not None

        # Rollback
        await test_session.rollback()

        # Verify it doesn't exist after rollback
        from sqlalchemy import select

        query = select(OptionSnapshot).where(OptionSnapshot.id == snapshot_id)
        result = await test_session.execute(query)
        assert result.scalar_one_or_none() is None

    async def test_transaction_commit(self, test_session):
        """Test that transactions can be committed."""
        snapshot = OptionSnapshot(
            symbol="AAPL",
            timestamp=datetime.utcnow(),
            underlying_price=150.0,
            contracts_data=[],
        )

        test_session.add(snapshot)
        await test_session.commit()

        # Verify it exists after commit
        snapshot_id = snapshot.id
        from sqlalchemy import select

        query = select(OptionSnapshot).where(OptionSnapshot.id == snapshot_id)
        result = await test_session.execute(query)
        assert result.scalar_one_or_none() is not None
