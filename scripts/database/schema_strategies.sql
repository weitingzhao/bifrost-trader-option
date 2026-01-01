-- ============================================================================
-- BIFROST TRADER OPTION - STRATEGIES APP SCHEMA
-- ============================================================================
-- 
-- Schema for app_django/apps/strategies/models.py
-- 
-- Tables:
--   - strategy_history: Historical strategy analysis results
--   - market_conditions: Market state snapshots (SP500, VIX, etc.)
-- 
-- Last Updated: 2026-01-01
-- PostgreSQL Version: 17
-- TimescaleDB Version: 2.x
-- 
-- ============================================================================

-- ============================================================================
-- TABLE: strategy_history
-- Description: Historical strategy analysis results
-- Django Model: apps.strategies.models.StrategyHistory
-- ============================================================================
CREATE TABLE IF NOT EXISTS strategy_history (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    strategy_type VARCHAR(50) NOT NULL,
    parameters JSONB,
    entry_cost DOUBLE PRECISION NOT NULL,
    max_profit DOUBLE PRECISION NOT NULL,
    max_loss DOUBLE PRECISION NOT NULL,
    breakeven_points JSONB,
    profit_profile JSONB,
    delta DOUBLE PRECISION,
    gamma DOUBLE PRECISION,
    theta DOUBLE PRECISION,
    vega DOUBLE PRECISION,
    probability_of_profit DOUBLE PRECISION,
    risk_reward_ratio DOUBLE PRECISION,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for strategy_history
CREATE INDEX IF NOT EXISTS idx_strategy_history_stock_id ON strategy_history(stock_id);
CREATE INDEX IF NOT EXISTS idx_strategy_history_symbol ON strategy_history(symbol);
CREATE INDEX IF NOT EXISTS idx_strategy_history_strategy_type ON strategy_history(strategy_type);
CREATE INDEX IF NOT EXISTS idx_strategy_history_timestamp ON strategy_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_strategy_history_created_at ON strategy_history(created_at);

-- Composite index for common queries (symbol, strategy_type, timestamp)
CREATE INDEX IF NOT EXISTS idx_strategy_history_symbol_type_timestamp 
    ON strategy_history(symbol, strategy_type, timestamp DESC);

-- ============================================================================
-- TABLE: market_conditions
-- Description: Market state snapshots (SP500, VIX, etc.)
-- Django Model: apps.strategies.models.MarketConditions
-- ============================================================================
CREATE TABLE IF NOT EXISTS market_conditions (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sp500_price DOUBLE PRECISION,
    vix DOUBLE PRECISION,
    market_trend VARCHAR(20),
    volatility_regime VARCHAR(20),
    meta_data JSONB
);

-- Indexes for market_conditions
CREATE INDEX IF NOT EXISTS idx_market_conditions_timestamp ON market_conditions(timestamp);

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================
COMMENT ON TABLE strategy_history IS 'Historical strategy analysis results (apps.strategies.models.StrategyHistory)';
COMMENT ON TABLE market_conditions IS 'Market state snapshots (apps.strategies.models.MarketConditions)';

