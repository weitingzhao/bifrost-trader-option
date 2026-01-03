"""Utility functions package."""
from .logger import setup_logging
from .pricing import (
    calculate_black_scholes_price,
    calculate_greeks,
    calculate_implied_volatility,
)
from .database_constants import (
    STOCKS_TABLE,
    OPTION_SNAPSHOTS_TABLE,
    OPTION_CONTRACTS_TABLE,
    STRATEGY_HISTORY_TABLE,
    MARKET_CONDITIONS_TABLE,
    COLLECTION_JOBS_TABLE,
    OPTION_TYPE_CALL,
    OPTION_TYPE_PUT,
    STRATEGY_TYPE_COVERED_CALL,
    STRATEGY_TYPE_IRON_CONDOR,
)

# Validators may not exist yet
try:
    from .validators import validate_symbol, validate_strike
    __all__ = [
        'setup_logging',
        'validate_symbol',
        'validate_strike',
        'calculate_black_scholes_price',
        'calculate_greeks',
        'calculate_implied_volatility',
        'STOCKS_TABLE',
        'OPTION_SNAPSHOTS_TABLE',
        'OPTION_CONTRACTS_TABLE',
        'STRATEGY_HISTORY_TABLE',
        'MARKET_CONDITIONS_TABLE',
        'COLLECTION_JOBS_TABLE',
        'OPTION_TYPE_CALL',
        'OPTION_TYPE_PUT',
        'STRATEGY_TYPE_COVERED_CALL',
        'STRATEGY_TYPE_IRON_CONDOR',
    ]
except ImportError:
    __all__ = [
        'setup_logging',
        'calculate_black_scholes_price',
        'calculate_greeks',
        'calculate_implied_volatility',
        'STOCKS_TABLE',
        'OPTION_SNAPSHOTS_TABLE',
        'OPTION_CONTRACTS_TABLE',
        'STRATEGY_HISTORY_TABLE',
        'MARKET_CONDITIONS_TABLE',
        'COLLECTION_JOBS_TABLE',
        'OPTION_TYPE_CALL',
        'OPTION_TYPE_PUT',
        'STRATEGY_TYPE_COVERED_CALL',
        'STRATEGY_TYPE_IRON_CONDOR',
    ]
