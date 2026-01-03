"""Backtesting engine for options strategies."""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import pandas as pd
import numpy as np

from app_api.database.schemas import StrategyResult, StrategyType
from ..strategies.base_strategy import BaseStrategy
from .models import BacktestResult

logger = logging.getLogger(__name__)


class StrategyBacktester:
    """Backtesting engine for options strategies."""
    
    def __init__(self, use_vectorbt: bool = True):
        """
        Initialize backtester.
        
        Args:
            use_vectorbt: Use VectorBT engine (default: True)
        """
        self.use_vectorbt = use_vectorbt
        self.engine = None
        if use_vectorbt:
            try:
                from .vectorbt_engine import VectorBTEngine
                self.engine = VectorBTEngine()
            except ImportError:
                logger.warning("VectorBT not available, falling back to simple backtesting")
                self.use_vectorbt = False
    
    def backtest_strategy(
        self,
        strategy: BaseStrategy,
        historical_data: pd.DataFrame,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        initial_capital: float = 10000.0
    ) -> BacktestResult:
        """
        Backtest a strategy using historical data.
        
        Args:
            strategy: Strategy instance to backtest
            historical_data: DataFrame with columns: timestamp, underlying_price, option_data
            start_date: Start date for backtest (default: first date in data)
            end_date: End date for backtest (default: last date in data)
            initial_capital: Starting capital
            
        Returns:
            BacktestResult with performance metrics
        """
        if historical_data.empty:
            raise ValueError("Historical data is empty")
        
        # Filter date range
        if start_date:
            historical_data = historical_data[historical_data['timestamp'] >= start_date]
        if end_date:
            historical_data = historical_data[historical_data['timestamp'] <= end_date]
        
        if historical_data.empty:
            raise ValueError("No data in specified date range")
        
        start_date = start_date or historical_data['timestamp'].min()
        end_date = end_date or historical_data['timestamp'].max()
        
        if self.use_vectorbt and self.engine:
            return self._backtest_with_vectorbt(
                strategy, historical_data, start_date, end_date, initial_capital
            )
        else:
            return self._backtest_simple(
                strategy, historical_data, start_date, end_date, initial_capital
            )
    
    def _backtest_with_vectorbt(
        self,
        strategy: BaseStrategy,
        historical_data: pd.DataFrame,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float
    ) -> BacktestResult:
        """Backtest using VectorBT engine."""
        return self.engine.run_backtest(
            strategy=strategy,
            data=historical_data,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital
        )
    
    def _backtest_simple(
        self,
        strategy: BaseStrategy,
        historical_data: pd.DataFrame,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float
    ) -> BacktestResult:
        """Simple backtest without VectorBT."""
        equity = [initial_capital]
        trades = []
        current_capital = initial_capital
        
        for idx, row in historical_data.iterrows():
            underlying_price = row.get('underlying_price', 0)
            if underlying_price <= 0:
                continue
            
            # Calculate P&L at this price point
            pnl = strategy.calculate_profit_loss(underlying_price)
            
            # Update capital (simplified - assumes we can enter/exit at any time)
            current_capital = initial_capital + pnl
            equity.append(current_capital)
            
            trades.append({
                'timestamp': row.get('timestamp', idx),
                'underlying_price': underlying_price,
                'pnl': pnl,
                'capital': current_capital
            })
        
        # Calculate metrics
        equity_series = pd.Series(equity)
        total_return = (equity_series.iloc[-1] - initial_capital) / initial_capital * 100
        
        # Calculate max drawdown
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max
        max_drawdown = drawdown.min() * 100 if not drawdown.empty else None
        
        # Calculate win rate
        profitable = sum(1 for t in trades if t['pnl'] > 0)
        win_rate = (profitable / len(trades) * 100) if trades else None
        
        return BacktestResult(
            strategy_type=strategy.strategy_type,
            symbol=strategy.symbol,
            start_date=start_date,
            end_date=end_date,
            total_return=total_return,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            total_trades=len(trades),
            profitable_trades=profitable,
            equity_curve=equity_series,
            trades=trades
        )
    
    def compare_strategies(
        self,
        strategies: List[BaseStrategy],
        historical_data: pd.DataFrame,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        initial_capital: float = 10000.0
    ) -> List[BacktestResult]:
        """
        Compare multiple strategies.
        
        Args:
            strategies: List of strategy instances
            historical_data: Historical data for backtesting
            start_date: Start date
            end_date: End date
            initial_capital: Starting capital
            
        Returns:
            List of BacktestResult objects
        """
        results = []
        for strategy in strategies:
            try:
                result = self.backtest_strategy(
                    strategy, historical_data, start_date, end_date, initial_capital
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error backtesting {strategy.strategy_type}: {e}")
                continue
        
        return results

