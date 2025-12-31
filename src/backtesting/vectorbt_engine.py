"""VectorBT engine for fast vectorized backtesting."""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import pandas as pd
import numpy as np

try:
    import vectorbt as vbt
    VECTORBT_AVAILABLE = True
except ImportError:
    VECTORBT_AVAILABLE = False
    logging.warning("VectorBT not available. Install with: pip install vectorbt>=0.25.0")

from ..strategies.base_strategy import BaseStrategy
from ..database.schemas import StrategyType
from .models import BacktestResult

logger = logging.getLogger(__name__)


class VectorBTEngine:
    """VectorBT-based backtesting engine for options strategies."""
    
    def __init__(self):
        """Initialize VectorBT engine."""
        if not VECTORBT_AVAILABLE:
            raise ImportError("VectorBT is not installed. Install with: pip install vectorbt>=0.25.0")
        self.vbt = vbt
    
    def run_backtest(
        self,
        strategy: BaseStrategy,
        data: pd.DataFrame,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 10000.0
    ) -> BacktestResult:
        """
        Run backtest using VectorBT.
        
        Args:
            strategy: Strategy instance to backtest
            data: Historical data DataFrame
            start_date: Start date
            end_date: End date
            initial_capital: Starting capital
            
        Returns:
            BacktestResult with performance metrics
        """
        # Prepare data
        if 'timestamp' in data.columns:
            data = data.set_index('timestamp')
        
        # Ensure we have underlying_price column
        if 'underlying_price' not in data.columns:
            raise ValueError("Historical data must contain 'underlying_price' column")
        
        # Calculate P&L for each time point
        pnl_series = data['underlying_price'].apply(
            lambda price: strategy.calculate_profit_loss(price)
        )
        
        # Calculate equity curve
        equity = initial_capital + pnl_series.cumsum()
        
        # Calculate returns
        returns = pnl_series / initial_capital
        
        # Calculate metrics using VectorBT
        portfolio = self.vbt.Portfolio.from_returns(
            returns,
            init_cash=initial_capital,
            freq='D'  # Daily frequency
        )
        
        # Extract metrics
        total_return = portfolio.total_return() * 100
        sharpe_ratio = portfolio.sharpe_ratio()
        max_drawdown = portfolio.max_drawdown() * 100
        
        # Calculate win rate
        profitable_periods = (pnl_series > 0).sum()
        total_periods = len(pnl_series)
        win_rate = (profitable_periods / total_periods * 100) if total_periods > 0 else None
        
        # Prepare trades list
        trades = []
        for idx, (timestamp, row) in enumerate(data.iterrows()):
            trades.append({
                'timestamp': timestamp.isoformat() if isinstance(timestamp, pd.Timestamp) else str(timestamp),
                'underlying_price': row.get('underlying_price', 0),
                'pnl': pnl_series.iloc[idx] if idx < len(pnl_series) else 0,
                'equity': equity.iloc[idx] if idx < len(equity) else initial_capital
            })
        
        return BacktestResult(
            strategy_type=strategy.strategy_type,
            symbol=strategy.symbol,
            start_date=start_date,
            end_date=end_date,
            total_return=total_return,
            sharpe_ratio=float(sharpe_ratio) if sharpe_ratio is not None and not pd.isna(sharpe_ratio) else None,
            max_drawdown=float(max_drawdown) if max_drawdown is not None and not pd.isna(max_drawdown) else None,
            win_rate=win_rate,
            total_trades=total_periods,
            profitable_trades=int(profitable_periods),
            equity_curve=equity,
            trades=trades
        )
    
    def optimize_parameters(
        self,
        strategy_class: type,
        data: pd.DataFrame,
        parameter_ranges: Dict[str, list],
        initial_capital: float = 10000.0
    ) -> Dict[str, Any]:
        """
        Optimize strategy parameters using VectorBT.
        
        Args:
            strategy_class: Strategy class to optimize
            data: Historical data
            parameter_ranges: Dictionary of parameter names to value ranges
            initial_capital: Starting capital
            
        Returns:
            Dictionary with optimal parameters and results
        """
        if not VECTORBT_AVAILABLE:
            raise ImportError("VectorBT is required for parameter optimization")
        
        # This is a placeholder - full optimization would require more complex setup
        # VectorBT supports parameter optimization through its portfolio optimization features
        logger.info("Parameter optimization requires full VectorBT portfolio setup")
        
        return {
            'status': 'not_implemented',
            'message': 'Full parameter optimization requires additional VectorBT portfolio configuration'
        }

