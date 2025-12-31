"""Backtesting API endpoints."""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from datetime import datetime, timedelta
import logging
import pandas as pd

from ...database.connection import get_db
from ...database.repositories.history_repo import get_history_repository
from ...database.schemas import StrategyType, CoveredCallParams, IronCondorParams, OptionContract, OptionType
from ...backtesting.backtester import StrategyBacktester
from ...strategies.covered_call import CoveredCall
from ...strategies.iron_condor import IronCondor
from ...analyzer.analyzer import get_analyzer
from ...core.options_chain import get_fetcher
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/api/backtesting/run")
async def run_backtest(
    strategy_params: dict,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    initial_capital: float = Query(10000.0, description="Initial capital"),
    db: AsyncSession = Depends(get_db)
):
    """
    Run backtest for a strategy using historical data.
    
    Args:
        strategy_params: Strategy parameters (same format as analyze endpoint)
        start_date: Start date for backtest
        end_date: End date for backtest
        initial_capital: Starting capital
        
    Returns:
        Backtest results with performance metrics
    """
    try:
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        if not start:
            start = datetime.utcnow() - timedelta(days=30)
        if not end:
            end = datetime.utcnow()
        
        # Get strategy type
        strategy_type = strategy_params.get('strategy_type')
        symbol = strategy_params.get('symbol')
        
        if not strategy_type or not symbol:
            raise HTTPException(status_code=400, detail="strategy_type and symbol are required")
        
        # For backtesting, we need to create a strategy instance that can work with historical prices
        # Since we need option contracts, we'll use the first snapshot to get contract data
        repo = get_history_repository(db)
        snapshots = await repo.get_option_snapshots(
            symbol=symbol,
            start_time=start,
            end_time=end,
            limit=1000
        )
        
        if not snapshots:
            raise HTTPException(
                status_code=404,
                detail=f"No historical data found for {symbol} in the specified date range"
            )
        
        # Get the first snapshot to extract option contract data
        first_snapshot = snapshots[0]
        contracts_data = first_snapshot.contracts_data if first_snapshot.contracts_data else []
        
        # Create strategy instance based on type
        strategy = None
        if strategy_type == 'covered_call':
            params = CoveredCallParams(**strategy_params)
            
            # Find matching call contract from historical data
            call_contract_data = None
            for contract in contracts_data:
                if (contract.get('expiration') == params.call_expiration and
                    contract.get('strike') == params.call_strike and
                    contract.get('option_type') == 'CALL'):
                    call_contract_data = contract
                    break
            
            if not call_contract_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Call contract not found: strike={params.call_strike}, exp={params.call_expiration}"
                )
            
            call_contract = OptionContract(**call_contract_data)
            stock_price = params.stock_price or first_snapshot.underlying_price
            
            strategy = CoveredCall.from_params(
                params=params,
                call_contract=call_contract,
                stock_price=stock_price
            )
            
        elif strategy_type == 'iron_condor':
            params = IronCondorParams(**strategy_params)
            
            # Find matching contracts
            put_sell_data = None
            put_buy_data = None
            call_sell_data = None
            call_buy_data = None
            
            for contract in contracts_data:
                if contract.get('expiration') != params.expiration:
                    continue
                
                if (contract.get('option_type') == 'PUT' and
                    contract.get('strike') == params.put_sell_strike):
                    put_sell_data = contract
                elif (contract.get('option_type') == 'PUT' and
                      contract.get('strike') == params.put_buy_strike):
                    put_buy_data = contract
                elif (contract.get('option_type') == 'CALL' and
                      contract.get('strike') == params.call_sell_strike):
                    call_sell_data = contract
                elif (contract.get('option_type') == 'CALL' and
                      contract.get('strike') == params.call_buy_strike):
                    call_buy_data = contract
            
            if not all([put_sell_data, put_buy_data, call_sell_data, call_buy_data]):
                raise HTTPException(
                    status_code=404,
                    detail="One or more option contracts not found for iron condor"
                )
            
            strategy = IronCondor.from_params(
                params=params,
                put_sell_contract=OptionContract(**put_sell_data),
                put_buy_contract=OptionContract(**put_buy_data),
                call_sell_contract=OptionContract(**call_sell_data),
                call_buy_contract=OptionContract(**call_buy_data)
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown strategy type: {strategy_type}")
        
        # Convert to DataFrame
        historical_data = pd.DataFrame([
            {
                'timestamp': snapshot.timestamp,
                'underlying_price': snapshot.underlying_price,
                'contracts_data': snapshot.contracts_data
            }
            for snapshot in snapshots
        ])
        
        # Run backtest
        backtester = StrategyBacktester(use_vectorbt=True)
        result = backtester.backtest_strategy(
            strategy=strategy,
            historical_data=historical_data,
            start_date=start,
            end_date=end,
            initial_capital=initial_capital
        )
        
        return result.to_dict()
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error running backtest: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


@router.get("/api/backtesting/compare")
async def compare_strategies(
    symbol: str = Query(..., description="Stock symbol"),
    strategy_types: str = Query(..., description="Comma-separated strategy types"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    initial_capital: float = Query(10000.0, description="Initial capital"),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare multiple strategies using backtesting.
    
    Args:
        symbol: Stock symbol
        strategy_types: Comma-separated list of strategy types
        start_date: Start date
        end_date: End date
        initial_capital: Starting capital
        
    Returns:
        Comparison results for all strategies
    """
    try:
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        if not start:
            start = datetime.utcnow() - timedelta(days=30)
        if not end:
            end = datetime.utcnow()
        
        # Fetch historical data
        repo = get_history_repository(db)
        snapshots = await repo.get_option_snapshots(
            symbol=symbol,
            start_time=start,
            end_time=end,
            limit=1000
        )
        
        if not snapshots:
            raise HTTPException(
                status_code=404,
                detail=f"No historical data found for {symbol}"
            )
        
        # Convert to DataFrame
        historical_data = pd.DataFrame([
            {
                'timestamp': snapshot.timestamp,
                'underlying_price': snapshot.underlying_price,
                'contracts_data': snapshot.contracts_data
            }
            for snapshot in snapshots
        ])
        
        # This is a simplified comparison - in practice, you'd need strategy parameters
        # For now, return a placeholder response
        return {
            'message': 'Strategy comparison requires specific strategy parameters',
            'symbol': symbol,
            'strategies': strategy_types.split(','),
            'date_range': {
                'start': start.isoformat(),
                'end': end.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error comparing strategies: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

