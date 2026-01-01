-- ============================================================================
-- BIFROST TRADER OPTION - DATABASE SCHEMA (MASTER FILE)
-- ============================================================================
-- 
-- This is the master schema file that includes all app-specific schemas.
-- 
-- ⚠️  IMPORTANT: Django models are the SINGLE SOURCE OF TRUTH
-- 
-- Schema organization matches Django app structure:
--   - schema_options.sql: Options app (stocks, option_snapshots, option_contracts)
--   - schema_strategies.sql: Strategies app (strategy_history, market_conditions)
--   - schema_data_collection.sql: Data collection app (collection_jobs)
-- 
-- Workflow for database changes:
--   1. Update Django models (app_django/apps/*/models.py) ⭐ SINGLE SOURCE OF TRUTH
--   2. Generate Django migrations (python manage.py makemigrations)
--   3. Update SQLAlchemy models (src/database/models.py) to match Django models
--   4. Update app-specific schema files (schema_*.sql) to match Django models
--   5. Run verify_schema.py to verify all three are in sync
-- 
-- Last Updated: 2026-01-01
-- PostgreSQL Version: 17
-- TimescaleDB Version: 2.x
-- 
-- ============================================================================

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================================================
-- INCLUDE APP-SPECIFIC SCHEMAS
-- ============================================================================
-- 
-- The actual table definitions are in separate files organized by Django app:
-- 
-- 1. Options App (app_django/apps/options/)
--    \i schema_options.sql
--    - stocks
--    - option_snapshots
--    - option_contracts
-- 
-- 2. Strategies App (app_django/apps/strategies/)
--    \i schema_strategies.sql
--    - strategy_history
--    - market_conditions
-- 
-- 3. Data Collection App (app_django/apps/data_collection/)
--    \i schema_data_collection.sql
--    - collection_jobs
-- 
-- Note: In PostgreSQL, you can include files using:
--   psql -f schema.sql (will execute all files)
--   Or use \i commands in psql interactive mode
-- 
-- For automated scripts, concatenate all files:
--   cat schema_options.sql schema_strategies.sql schema_data_collection.sql > schema_all.sql
-- 
-- ============================================================================

-- Load Options App Schema
\i schema_options.sql

-- Load Strategies App Schema
\i schema_strategies.sql

-- Load Data Collection App Schema
\i schema_data_collection.sql

-- ============================================================================
-- TIMESCALEDB HYPERTABLE SETUP
-- ============================================================================
-- Run this after creating the option_snapshots table
-- SELECT create_hypertable('option_snapshots', 'timestamp', if_not_exists => TRUE);

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

