"""SQLAlchemy ORM models matching Django models."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from .connection import Base


class Stock(Base):
    """Stock symbol and metadata (mirrors Django apps.options.models.Stock)."""
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=True)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    option_snapshots = relationship("OptionSnapshot", back_populates="stock")
    strategies = relationship("StrategyHistory", back_populates="stock")


class OptionSnapshot(Base):
    """TimescaleDB hypertable for option chain snapshots (mirrors Django apps.options.models.OptionSnapshot)."""
    __tablename__ = 'option_snapshots'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    symbol = Column(String(10), index=True, nullable=False)
    underlying_price = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.now(), index=True, nullable=False)
    
    # Exchange information
    exchange = Column(String(20), nullable=True, index=True)
    
    # JSON fields for flexible data storage
    contracts_data = Column(JSON, default=list)
    expiration_dates = Column(JSON, default=list)
    strike_range = Column(JSON, default=dict)
    
    # Relationships
    stock = relationship("Stock", back_populates="option_snapshots")
    contracts = relationship("OptionContract", back_populates="snapshot")
    
    __table_args__ = (
        Index('idx_option_snapshots_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_option_snapshots_timestamp', 'timestamp'),
    )


class OptionContract(Base):
    """Individual option contract (mirrors Django apps.options.models.OptionContract)."""
    __tablename__ = 'option_contracts'
    
    id = Column(Integer, primary_key=True)
    snapshot_id = Column(Integer, ForeignKey('option_snapshots.id'), nullable=False)
    symbol = Column(String(10), index=True, nullable=False)
    strike = Column(Float, index=True, nullable=False)
    expiration = Column(String(8), index=True, nullable=False)  # YYYYMMDD format
    option_type = Column(String(4), nullable=False)  # 'CALL' or 'PUT'
    
    # Pricing data
    bid = Column(Float, nullable=False)
    ask = Column(Float, nullable=False)
    last = Column(Float, nullable=True)
    mid_price = Column(Float, nullable=True)
    
    # Volume and open interest
    volume = Column(Integer, default=0)
    open_interest = Column(Integer, default=0)
    
    # Greeks
    implied_volatility = Column(Float, nullable=True)
    delta = Column(Float, nullable=True)
    gamma = Column(Float, nullable=True)
    theta = Column(Float, nullable=True)
    vega = Column(Float, nullable=True)
    
    # IB contract ID
    contract_id = Column(Integer, unique=True, nullable=True)
    
    # Exchange information
    exchange = Column(String(20), nullable=True, index=True)
    
    timestamp = Column(DateTime(timezone=True), default=func.now(), index=True, nullable=False)
    
    # Relationships
    snapshot = relationship("OptionSnapshot", back_populates="contracts")
    
    __table_args__ = (
        Index('idx_option_contracts_symbol_exp_strike', 'symbol', 'expiration', 'strike'),
        Index('idx_option_contracts_timestamp', 'timestamp'),
        UniqueConstraint('symbol', 'strike', 'expiration', 'option_type', 'timestamp', name='uq_option_contract'),
    )


class StrategyHistory(Base):
    """Historical strategy analysis results (mirrors Django apps.strategies.models.StrategyHistory)."""
    __tablename__ = 'strategy_history'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    symbol = Column(String(10), index=True, nullable=False)
    strategy_type = Column(String(50), index=True, nullable=False)
    
    # Strategy parameters (JSON)
    parameters = Column(JSON, default=dict)
    
    # Analysis results
    entry_cost = Column(Float, nullable=False)
    max_profit = Column(Float, nullable=False)
    max_loss = Column(Float, nullable=False)
    breakeven_points = Column(JSON, default=list)
    profit_profile = Column(JSON, default=list)
    
    # Greeks
    delta = Column(Float, nullable=True)
    gamma = Column(Float, nullable=True)
    theta = Column(Float, nullable=True)
    vega = Column(Float, nullable=True)
    
    # Metrics
    probability_of_profit = Column(Float, nullable=True)
    risk_reward_ratio = Column(Float, nullable=True)
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), default=func.now(), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    stock = relationship("Stock", back_populates="strategies")
    
    __table_args__ = (
        Index('idx_strategy_history_symbol_type_timestamp', 'symbol', 'strategy_type', 'timestamp'),
        Index('idx_strategy_history_timestamp', 'timestamp'),
    )


class MarketConditions(Base):
    """Market state snapshots (mirrors Django apps.strategies.models.MarketConditions)."""
    __tablename__ = 'market_conditions'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), default=func.now(), index=True, nullable=False)
    
    # Market indices
    sp500_price = Column(Float, nullable=True)
    vix = Column(Float, nullable=True)
    
    # Market conditions
    market_trend = Column(String(20), nullable=True)
    volatility_regime = Column(String(20), nullable=True)
    
    # Additional metadata (renamed to avoid SQLAlchemy reserved word)
    meta_data = Column(JSON, default=dict)
    
    __table_args__ = (
        Index('idx_market_conditions_timestamp', 'timestamp'),
    )


class CollectionJob(Base):
    """Track data collection jobs (mirrors Django apps.data_collection.models.CollectionJob)."""
    __tablename__ = 'collection_jobs'
    
    id = Column(Integer, primary_key=True)
    job_type = Column(String(50), index=True, nullable=False)
    symbol = Column(String(10), index=True, nullable=True)
    exchange = Column(String(20), index=True, nullable=True)
    status = Column(String(20), nullable=False, default='pending')
    
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Job metadata
    records_collected = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    __table_args__ = (
        Index('idx_collection_jobs_type_status_created', 'job_type', 'status', 'created_at'),
    )
