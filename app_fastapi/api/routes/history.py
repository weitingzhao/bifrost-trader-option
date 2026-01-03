"""Historical data routes."""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
import logging

from app_fastapi.database.connection import get_db
from app_fastapi.database.repositories.history_repo import get_history_repository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/history/options/{symbol}")
async def get_option_history(
    symbol: str,
    hours: int = Query(24, ge=1, le=168, description="Number of hours of history"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical option data for a symbol.
    
    Args:
        symbol: Stock symbol
        hours: Number of hours of history to retrieve
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of option snapshots with timestamps
    """
    try:
        repo = get_history_repository(db)
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        snapshots = await repo.get_option_snapshots(
            symbol=symbol,
            start_time=start_time,
            end_time=end_time,
        limit=limit
        )
        
        return {
            "symbol": symbol,
            "count": len(snapshots),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "snapshots": [
                {
                    "timestamp": snapshot.timestamp.isoformat(),
                    "underlying_price": snapshot.underlying_price,
                    "contract_count": len(snapshot.contracts_data) if snapshot.contracts_data else 0,
                }
                for snapshot in snapshots
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching option history for {symbol}: {e}", exc_info=True)
        return {
            "error": "Failed to fetch historical data",
            "message": str(e),
            "symbol": symbol
        }


@router.get("/api/history/strategies")
async def get_strategy_history(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    strategy_type: Optional[str] = Query(None, description="Filter by strategy type"),
    hours: int = Query(24, ge=1, le=168, description="Number of hours of history"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical strategy analysis results.
    
    Args:
        symbol: Stock symbol filter (optional)
        strategy_type: Strategy type filter (optional)
        hours: Number of hours of history to retrieve
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of strategy history records
    """
    try:
        repo = get_history_repository(db)
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        strategies = await repo.get_strategy_history(
            symbol=symbol,
            strategy_type=strategy_type,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        return {
            "count": len(strategies),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "strategies": [
                {
                    "id": strategy.id,
                    "symbol": strategy.symbol,
                    "strategy_type": strategy.strategy_type,
                    "entry_cost": strategy.entry_cost,
                    "max_profit": strategy.max_profit,
                    "max_loss": strategy.max_loss,
                    "risk_reward_ratio": strategy.risk_reward_ratio,
                    "timestamp": strategy.timestamp.isoformat(),
                }
                for strategy in strategies
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching strategy history: {e}", exc_info=True)
        return {
            "error": "Failed to fetch strategy history",
            "message": str(e)
        }

