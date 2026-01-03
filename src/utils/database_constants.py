"""Shared database constants and table names."""
# Table names (must match Django models db_table)
STOCKS_TABLE = 'stocks'
OPTION_SNAPSHOTS_TABLE = 'option_snapshots'
OPTION_CONTRACTS_TABLE = 'option_contracts'
STRATEGY_HISTORY_TABLE = 'strategy_history'
MARKET_CONDITIONS_TABLE = 'market_conditions'
COLLECTION_JOBS_TABLE = 'collection_jobs'

# Column names (for reference)
OPTION_TYPE_CALL = 'CALL'
OPTION_TYPE_PUT = 'PUT'

STRATEGY_TYPE_COVERED_CALL = 'covered_call'
STRATEGY_TYPE_IRON_CONDOR = 'iron_condor'

