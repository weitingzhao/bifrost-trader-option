-- ============================================================================
-- BIFROST TRADER OPTION - OPTIONS APP SCHEMA
-- ============================================================================
-- 
-- Schema for app_django/apps/options/models.py
-- 
-- Tables:
--   - stocks: Stock symbols and metadata
--   - option_snapshots: TimescaleDB hypertable for option chain snapshots
--   - option_contracts: Individual option contracts from option chains
-- 
-- Last Updated: 2026-01-01
-- PostgreSQL Version: 17
-- TimescaleDB Version: 2.x
-- 
-- ============================================================================

-- ============================================================================
-- TABLE: stocks
-- Description: Stock symbols and metadata
-- Django Model: apps.options.models.Stock
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
-- Django Model: apps.options.models.OptionSnapshot
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

-- Composite index for common queries (symbol + timestamp)
CREATE INDEX IF NOT EXISTS idx_option_snapshots_symbol_timestamp 
    ON option_snapshots(symbol, timestamp DESC);

-- Convert to TimescaleDB hypertable (run this after table creation)
-- SELECT create_hypertable('option_snapshots', 'timestamp', if_not_exists => TRUE);

-- ============================================================================
-- TABLE: option_contracts
-- Description: Individual option contracts from option chains
-- Django Model: apps.options.models.OptionContract
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

-- Composite index for common queries (symbol, expiration, strike)
CREATE INDEX IF NOT EXISTS idx_option_contracts_symbol_expiration_strike 
    ON option_contracts(symbol, expiration, strike);

-- Unique constraint for option contracts
CREATE UNIQUE INDEX IF NOT EXISTS uq_option_contract 
    ON option_contracts(symbol, strike, expiration, option_type, timestamp);

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================
COMMENT ON TABLE stocks IS 'Stock symbols and metadata (apps.options.models.Stock)';
COMMENT ON TABLE option_snapshots IS 'TimescaleDB hypertable for option chain snapshots (apps.options.models.OptionSnapshot)';
COMMENT ON TABLE option_contracts IS 'Individual option contracts from option chains (apps.options.models.OptionContract)';

