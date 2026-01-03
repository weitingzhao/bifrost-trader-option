"""Repository for collection job operations."""
import logging
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app_fastapi.database.models import CollectionJob

logger = logging.getLogger(__name__)


class CollectionJobRepository:
    """Repository for collection job operations."""
    
    @staticmethod
    async def create_job(
        job_type: str,
        symbol: Optional[str],
        exchange: Optional[str],
        db: AsyncSession
    ) -> CollectionJob:
        """
        Create a new collection job.
        
        Args:
            job_type: Type of job (e.g., 'option_chain')
            symbol: Stock symbol (optional)
            exchange: Exchange name (optional)
            db: Database session
            
        Returns:
            Created CollectionJob
        """
        job = CollectionJob(
            job_type=job_type,
            symbol=symbol,
            exchange=exchange,
            status='pending',
            created_at=datetime.now(),
        )
        
        db.add(job)
        await db.flush()
        
        logger.info(f"Created collection job {job.id} for {job_type} - {symbol or 'all'}")
        return job
    
    @staticmethod
    async def update_job_status(
        job_id: int,
        status: str,
        error_message: Optional[str] = None,
        records_collected: int = 0,
        db: AsyncSession = None
    ) -> Optional[CollectionJob]:
        """
        Update job status and metadata.
        
        Args:
            job_id: Job ID
            status: New status ('pending', 'running', 'completed', 'failed')
            error_message: Optional error message
            records_collected: Number of records collected
            db: Database session
            
        Returns:
            Updated CollectionJob or None if not found
        """
        result = await db.execute(
            select(CollectionJob).where(CollectionJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            logger.warning(f"Job {job_id} not found")
            return None
        
        job.status = status
        job.records_collected = records_collected
        
        if error_message:
            job.error_message = error_message
        
        if status == 'running' and not job.started_at:
            job.started_at = datetime.now()
        elif status in ['completed', 'failed']:
            job.completed_at = datetime.now()
        
        await db.flush()
        
        logger.info(f"Updated job {job_id} status to {status} (records: {records_collected})")
        return job
    
    @staticmethod
    async def get_job(
        job_id: int,
        db: AsyncSession
    ) -> Optional[CollectionJob]:
        """
        Get a job by ID.
        
        Args:
            job_id: Job ID
            db: Database session
            
        Returns:
            CollectionJob or None
        """
        result = await db.execute(
            select(CollectionJob).where(CollectionJob.id == job_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_jobs(
        filters: Optional[Dict] = None,
        limit: int = 100,
        offset: int = 0,
        db: AsyncSession = None
    ) -> List[CollectionJob]:
        """
        List collection jobs with optional filters.
        
        Args:
            filters: Optional filters dict with keys: status, symbol, job_type, exchange
            limit: Maximum number of results
            offset: Offset for pagination
            db: Database session
            
        Returns:
            List of CollectionJob objects
        """
        query = select(CollectionJob)
        
        if filters:
            conditions = []
            
            if 'status' in filters:
                conditions.append(CollectionJob.status == filters['status'])
            
            if 'symbol' in filters:
                conditions.append(CollectionJob.symbol == filters['symbol'])
            
            if 'job_type' in filters:
                conditions.append(CollectionJob.job_type == filters['job_type'])
            
            if 'exchange' in filters:
                conditions.append(CollectionJob.exchange == filters['exchange'])
            
            if conditions:
                query = query.where(and_(*conditions))
        
        query = query.order_by(CollectionJob.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        return list(result.scalars().all())

