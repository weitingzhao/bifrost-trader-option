"""Backtesting module for options strategies using VectorBT."""
from .backtester import StrategyBacktester
from .models import BacktestResult

__all__ = [
    'StrategyBacktester',
    'BacktestResult',
]

# Optional VectorBT engine (only imported if needed)
try:
    from .vectorbt_engine import VectorBTEngine
    __all__.append('VectorBTEngine')
except ImportError:
    pass

