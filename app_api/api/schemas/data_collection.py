"""Pydantic schemas for data collection API."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CollectionRequest(BaseModel):
    """Request schema for triggering data collection."""
    symbol: str = Field(..., description="Stock symbol to collect")
    exchange: Optional[str] = Field(None, description="Optional exchange specification (auto-detected if not provided)")
    store_contracts: bool = Field(True, description="Whether to store normalized contracts in addition to snapshot")


class BatchCollectionRequest(BaseModel):
    """Request schema for batch collection."""
    symbols: List[str] = Field(..., description="List of stock symbols to collect")
    store_contracts: bool = Field(True, description="Whether to store normalized contracts")


class CollectionJobResponse(BaseModel):
    """Response schema for collection job status."""
    id: int
    job_type: str
    symbol: Optional[str]
    exchange: Optional[str]
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    records_collected: int = 0
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class CollectionResponse(BaseModel):
    """Response schema for collection request."""
    job_id: int
    status: str
    symbol: str
    exchange: Optional[str] = None
    message: Optional[str] = None


class BatchCollectionResponse(BaseModel):
    """Response schema for batch collection."""
    status: str
    total: int
    results: List[CollectionResponse]


class CollectionJobsListResponse(BaseModel):
    """Response schema for paginated job list."""
    jobs: List[CollectionJobResponse]
    total: int
    limit: int
    offset: int

