"""Repository for historical data access."""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app_fastapi.database.models import OptionSnapshot, StrategyHistory, Stock
from app_fastapi.database.schemas import OptionsChain, StrategyResult

logger = None  # Will be initialized when needed


class HistoryRepository:
    """Repository for accessing historical data."""
    
    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db
    
    async def get_option_snapshots(
        self,
        symbol: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[OptionSnapshot]:
        """
        Get option snapshots for a symbol within a time range.
        
        Args:
            symbol: Stock symbol
            start_time: Start of time range (defaults to 24 hours ago)
            end_time: End of time range (defaults to now)
            limit: Maximum number of records to return
            
        Returns:
            List of OptionSnapshot objects
        """
        if end_time is None:
            end_time = datetime.utcnow()
        if start_time is None:
            start_time = end_time - timedelta(hours=24)
        
        query = select(OptionSnapshot).where(
            and_(
                OptionSnapshot.symbol == symbol,
                OptionSnapshot.timestamp >= start_time,
                OptionSnapshot.timestamp <= end_time
            )
        ).order_by(OptionSnapshot.timestamp.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_strategy_history(
        self,
        symbol: Optional[str] = None,
        strategy_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[StrategyHistory]:
        """
        Get strategy history records.
        
        Args:
            symbol: Filter by symbol (optional)
            strategy_type: Filter by strategy type (optional)
            start_time: Start of time range (optional)
            end_time: End of time range (optional)
            limit: Maximum number of records to return
            
        Returns:
            List of StrategyHistory objects
        """
        conditions = []
        
        if symbol:
            conditions.append(StrategyHistory.symbol == symbol)
        if strategy_type:
            conditions.append(StrategyHistory.strategy_type == strategy_type)
        if start_time:
            conditions.append(StrategyHistory.timestamp >= start_time)
        if end_time:
            conditions.append(StrategyHistory.timestamp <= end_time)
        
        query = select(StrategyHistory)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(StrategyHistory.timestamp.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()


def get_history_repository(db: AsyncSession) -> HistoryRepository:
    """Get a history repository instance."""
    return HistoryRepository(db)

