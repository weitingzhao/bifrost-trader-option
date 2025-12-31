-- TimescaleDB hypertable setup for option_snapshots
-- Run this after Django migrations have created the tables
-- Execute: psql -U bifrost -d options_db -f setup_timescaledb.sql

-- Connect to the database (should already be connected)
\c options_db

-- Verify TimescaleDB extension is installed
SELECT * FROM pg_extension WHERE extname = 'timescaledb';

-- Convert option_snapshots table to hypertable
-- Note: The table must exist first (created by Django migrations)
-- This will convert the existing table to a TimescaleDB hypertable

-- First, check if the table exists
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'option_snapshots') THEN
        -- Convert to hypertable with timestamp as time column
        PERFORM create_hypertable('option_snapshots', 'timestamp', 
            chunk_time_interval => INTERVAL '1 day',
            if_not_exists => TRUE);
        
        RAISE NOTICE 'Hypertable created successfully for option_snapshots';
    ELSE
        RAISE NOTICE 'Table option_snapshots does not exist yet. Run Django migrations first.';
    END IF;
END $$;

-- Create additional indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_option_snapshots_symbol_timestamp 
    ON option_snapshots (symbol, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_option_snapshots_timestamp 
    ON option_snapshots (timestamp DESC);

-- Verify hypertable creation
SELECT * FROM timescaledb_information.hypertables WHERE hypertable_name = 'option_snapshots';

-- Show chunk information
SELECT * FROM timescaledb_information.chunks WHERE hypertable_name = 'option_snapshots';

