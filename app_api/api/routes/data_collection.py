"""Data collection API routes."""
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app_api.database.connection import get_db
from app_api.database.repositories import CollectionJobRepository
from app_api.api.schemas.data_collection import (
    CollectionRequest,
    CollectionResponse,
    CollectionJobResponse,
    CollectionJobsListResponse,
    BatchCollectionRequest,
    BatchCollectionResponse
)
# Import directly to avoid app_api.services.__init__.py celery dependency
from app_api.services.ib_data_collector import get_collector

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/api/data-collection/collect", response_model=CollectionResponse)
async def collect_option_chain(
    request: CollectionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger on-demand option chain collection for a symbol.
    
    Args:
        request: Collection request with symbol and options
        db: Database session
        
    Returns:
        CollectionResponse with job_id and status
    """
    try:
        collector = await get_collector()
        
        # Start collection (runs asynchronously)
        result = await collector.collect_option_chain_on_demand(
            symbol=request.symbol,
            exchange=request.exchange,
            store_contracts=request.store_contracts
        )
        
        if result['status'] == 'error':
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Collection failed')
            )
        
        return CollectionResponse(
            job_id=result['job_id'],
            status=result['status'],
            symbol=result['symbol'],
            exchange=result.get('exchange'),
            message=f"Collection job {result['job_id']} created"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering collection for {request.symbol}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/api/data-collection/jobs/{job_id}", response_model=CollectionJobResponse)
async def get_job_status(
    job_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get status of a collection job.
    
    Args:
        job_id: Job ID
        db: Database session
        
    Returns:
        CollectionJobResponse with job details
    """
    try:
        job = await CollectionJobRepository.get_job(job_id, db)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found"
            )
        
        return CollectionJobResponse(
            id=job.id,
            job_type=job.job_type,
            symbol=job.symbol,
            exchange=job.exchange,
            status=job.status,
            started_at=job.started_at,
            completed_at=job.completed_at,
            created_at=job.created_at,
            records_collected=job.records_collected or 0,
            error_message=job.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/api/data-collection/jobs", response_model=CollectionJobsListResponse)
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db)
):
    """
    List collection jobs with optional filters.
    
    Args:
        status: Optional status filter
        symbol: Optional symbol filter
        job_type: Optional job type filter
        limit: Maximum number of results
        offset: Offset for pagination
        db: Database session
        
    Returns:
        CollectionJobsListResponse with paginated job list
    """
    try:
        filters = {}
        if status:
            filters['status'] = status
        if symbol:
            filters['symbol'] = symbol.upper()
        if job_type:
            filters['job_type'] = job_type
        if exchange:
            filters['exchange'] = exchange
        
        jobs = await CollectionJobRepository.list_jobs(filters, limit, offset, db)
        
        # Get total count (simplified - in production, use count query)
        total_jobs = await CollectionJobRepository.list_jobs(filters=filters, limit=10000, offset=0, db=db)
        total = len(total_jobs)
        
        job_responses = [
            CollectionJobResponse(
                id=job.id,
                job_type=job.job_type,
                symbol=job.symbol,
                exchange=job.exchange,
                status=job.status,
                started_at=job.started_at,
                completed_at=job.completed_at,
                created_at=job.created_at,
                records_collected=job.records_collected or 0,
                error_message=job.error_message
            )
            for job in jobs
        ]
        
        return CollectionJobsListResponse(
            jobs=job_responses,
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error listing jobs: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/api/data-collection/collect-batch", response_model=BatchCollectionResponse)
async def collect_batch(
    request: BatchCollectionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger batch collection for multiple symbols.
    
    Args:
        request: Batch collection request
        db: Database session
        
    Returns:
        BatchCollectionResponse with results for each symbol
    """
    try:
        collector = await get_collector()
        
        # Start batch collection
        result = await collector.collect_option_chain_batch(
            symbols=request.symbols,
            store_contracts=request.store_contracts
        )
        
        # Convert results to response format
        responses = []
        for item in result['results']:
            if 'job_id' in item:
                responses.append(CollectionResponse(
                    job_id=item['job_id'],
                    status=item['status'],
                    symbol=item.get('symbol', ''),
                    exchange=item.get('exchange'),
                    message=item.get('error')
                ))
            else:
                responses.append(CollectionResponse(
                    job_id=0,
                    status=item.get('status', 'error'),
                    symbol=item.get('symbol', ''),
                    message=item.get('error', 'Unknown error')
                ))
        
        return BatchCollectionResponse(
            status=result['status'],
            total=result['total'],
            results=responses
        )
        
    except Exception as e:
        logger.error(f"Error in batch collection: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

