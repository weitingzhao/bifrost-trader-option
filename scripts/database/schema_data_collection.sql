-- ============================================================================
-- BIFROST TRADER OPTION - DATA COLLECTION APP SCHEMA
-- ============================================================================
-- 
-- Schema for app_django/apps/data_collection/models.py
-- 
-- Tables:
--   - collection_jobs: Data collection job tracking
-- 
-- Last Updated: 2026-01-01
-- PostgreSQL Version: 17
-- TimescaleDB Version: 2.x
-- 
-- ============================================================================

-- ============================================================================
-- TABLE: collection_jobs
-- Description: Data collection job tracking
-- Django Model: apps.data_collection.models.CollectionJob
-- ============================================================================
CREATE TABLE IF NOT EXISTS collection_jobs (
    id SERIAL PRIMARY KEY,
    job_type VARCHAR(50) NOT NULL,
    symbol VARCHAR(10),
    exchange VARCHAR(20),
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
CREATE INDEX IF NOT EXISTS idx_collection_jobs_exchange ON collection_jobs(exchange);
CREATE INDEX IF NOT EXISTS idx_collection_jobs_created_at ON collection_jobs(created_at);

-- Composite index for common queries (job_type, status, created_at)
CREATE INDEX IF NOT EXISTS idx_collection_jobs_type_status_created 
    ON collection_jobs(job_type, status, created_at DESC);

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================
COMMENT ON TABLE collection_jobs IS 'Data collection job tracking (apps.data_collection.models.CollectionJob)';

