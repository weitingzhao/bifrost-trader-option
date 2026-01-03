"""Backtesting data models."""
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd

from app_api.database.schemas import StrategyType


class BacktestResult:
    """Results from a backtest run."""
    
    def __init__(
        self,
        strategy_type: StrategyType,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        total_return: float,
        sharpe_ratio: Optional[float] = None,
        max_drawdown: Optional[float] = None,
        win_rate: Optional[float] = None,
        total_trades: int = 0,
        profitable_trades: int = 0,
        equity_curve: Optional[pd.Series] = None,
        trades: Optional[List[Dict[str, Any]]] = None
    ):
        """Initialize backtest result."""
        self.strategy_type = strategy_type
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.total_return = total_return
        self.sharpe_ratio = sharpe_ratio
        self.max_drawdown = max_drawdown
        self.win_rate = win_rate
        self.total_trades = total_trades
        self.profitable_trades = profitable_trades
        self.equity_curve = equity_curve
        self.trades = trades or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'strategy_type': self.strategy_type.value if hasattr(self.strategy_type, 'value') else str(self.strategy_type),
            'symbol': self.symbol,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'total_return': self.total_return,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': self.win_rate,
            'total_trades': self.total_trades,
            'profitable_trades': self.profitable_trades,
            'trades': self.trades,
        }

