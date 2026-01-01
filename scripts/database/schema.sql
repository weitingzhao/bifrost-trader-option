-- ============================================================================
-- BIFROST TRADER OPTION - DATABASE SCHEMA
-- ============================================================================
-- 
-- SINGLE SOURCE OF TRUTH FOR DATABASE SCHEMA
-- 
-- This file (scripts/database/schema.sql) is the authoritative database schema.
-- All database changes MUST start here, then:
--   1. Update Django models (django_app/apps/*/models.py)
--   2. Generate Django migrations (python manage.py makemigrations)
--   3. Update SQLAlchemy models (src/database/models.py) to match
--   4. Document changes in version tracking section below
-- 
-- Last Updated: 2026-01-01
-- PostgreSQL Version: 17
-- TimescaleDB Version: 2.x
-- 
-- ============================================================================

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================================================
-- TABLE: stocks
-- Description: Stock symbols and metadata
-- ============================================================================
CREATE TABLE IF NOT EXISTS stocks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(200),
    sector VARCHAR(100),
    industry VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for stocks
CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol);
CREATE INDEX IF NOT EXISTS idx_stocks_created_at ON stocks(created_at);

-- ============================================================================
-- TABLE: option_snapshots
-- Description: TimescaleDB hypertable for option chain snapshots
-- Note: This is a TimescaleDB hypertable for time-series data
-- ============================================================================
CREATE TABLE IF NOT EXISTS option_snapshots (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    underlying_price DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    contracts_data JSONB,
    expiration_dates JSONB,
    strike_range JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for option_snapshots
CREATE INDEX IF NOT EXISTS idx_option_snapshots_stock_id ON option_snapshots(stock_id);
CREATE INDEX IF NOT EXISTS idx_option_snapshots_symbol ON option_snapshots(symbol);
CREATE INDEX IF NOT EXISTS idx_option_snapshots_timestamp ON option_snapshots(timestamp);

-- Convert to TimescaleDB hypertable (run this after table creation)
-- SELECT create_hypertable('option_snapshots', 'timestamp', if_not_exists => TRUE);

-- ============================================================================
-- TABLE: option_contracts
-- Description: Individual option contracts from option chains
-- ============================================================================
CREATE TABLE IF NOT EXISTS option_contracts (
    id SERIAL PRIMARY KEY,
    snapshot_id INTEGER NOT NULL REFERENCES option_snapshots(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    strike DOUBLE PRECISION NOT NULL,
    expiration VARCHAR(8) NOT NULL,
    option_type VARCHAR(4) NOT NULL CHECK (option_type IN ('CALL', 'PUT')),
    bid DOUBLE PRECISION NOT NULL,
    ask DOUBLE PRECISION NOT NULL,
    last DOUBLE PRECISION,
    mid_price DOUBLE PRECISION,
    volume INTEGER,
    open_interest INTEGER,
    implied_volatility DOUBLE PRECISION,
    delta DOUBLE PRECISION,
    gamma DOUBLE PRECISION,
    theta DOUBLE PRECISION,
    vega DOUBLE PRECISION,
    contract_id INTEGER UNIQUE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for option_contracts
CREATE INDEX IF NOT EXISTS idx_option_contracts_snapshot_id ON option_contracts(snapshot_id);
CREATE INDEX IF NOT EXISTS idx_option_contracts_symbol ON option_contracts(symbol);
CREATE INDEX IF NOT EXISTS idx_option_contracts_timestamp ON option_contracts(timestamp);
CREATE INDEX IF NOT EXISTS idx_option_contracts_expiration ON option_contracts(expiration);
CREATE INDEX IF NOT EXISTS idx_option_contracts_strike ON option_contracts(strike);

-- Unique constraint for option contracts
CREATE UNIQUE INDEX IF NOT EXISTS uq_option_contract 
    ON option_contracts(symbol, strike, expiration, option_type, timestamp);

-- ============================================================================
-- TABLE: strategy_history
-- Description: Historical strategy analysis results
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

-- ============================================================================
-- TABLE: market_conditions
-- Description: Market state snapshots (SP500, VIX, etc.)
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
-- TABLE: collection_jobs
-- Description: Data collection job tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS collection_jobs (
    id SERIAL PRIMARY KEY,
    job_type VARCHAR(50) NOT NULL,
    symbol VARCHAR(10),
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    records_collected INTEGER,
    error_message TEXT
);

-- Indexes for collection_jobs
CREATE INDEX IF NOT EXISTS idx_collection_jobs_status ON collection_jobs(status);
CREATE INDEX IF NOT EXISTS idx_collection_jobs_job_type ON collection_jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_collection_jobs_symbol ON collection_jobs(symbol);
CREATE INDEX IF NOT EXISTS idx_collection_jobs_created_at ON collection_jobs(created_at);

-- ============================================================================
-- TIMESCALEDB HYPERTABLE SETUP
-- ============================================================================
-- Run this after creating the option_snapshots table
-- SELECT create_hypertable('option_snapshots', 'timestamp', if_not_exists => TRUE);

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================
COMMENT ON TABLE stocks IS 'Stock symbols and metadata';
COMMENT ON TABLE option_snapshots IS 'TimescaleDB hypertable for option chain snapshots (time-series data)';
COMMENT ON TABLE option_contracts IS 'Individual option contracts from option chains';
COMMENT ON TABLE strategy_history IS 'Historical strategy analysis results';
COMMENT ON TABLE market_conditions IS 'Market state snapshots (SP500, VIX, etc.)';
COMMENT ON TABLE collection_jobs IS 'Data collection job tracking';

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================
-- To track schema changes, add entries here:
-- 
-- Version 1.0.0 (2026-01-01)
--   - Initial schema creation
--   - All core tables: stocks, option_snapshots, option_contracts, 
--     strategy_history, market_conditions, collection_jobs
--   - TimescaleDB hypertable setup for option_snapshots
-- 
-- Future changes should be documented here with:
--   - Version number
--   - Date
--   - Description of changes
--   - Migration notes if needed
-- ============================================================================

