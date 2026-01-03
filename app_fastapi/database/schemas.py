"""Pydantic models for options data, strategies, and analysis results."""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class OptionType(str, Enum):
    """Option type enumeration."""
    CALL = "CALL"
    PUT = "PUT"


class StrategyType(str, Enum):
    """Strategy type enumeration."""
    COVERED_CALL = "covered_call"
    IRON_CONDOR = "iron_condor"


class OptionContract(BaseModel):
    """Options contract data model."""
    symbol: str
    strike: float
    expiration: str  # YYYYMMDD format
    option_type: OptionType
    bid: float
    ask: float
    last: Optional[float] = None
    volume: int = 0
    open_interest: int = 0
    implied_volatility: Optional[float] = None
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None
    contract_id: Optional[int] = None  # IB contract ID
    exchange: Optional[str] = None  # Exchange (OPRA, SMART, etc.)
    
    class Config:
        use_enum_values = True


class OptionsChain(BaseModel):
    """Options chain data model."""
    symbol: str
    underlying_price: float
    contracts: List[OptionContract]
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def get_contracts_by_expiration(self, expiration: str) -> List[OptionContract]:
        """Get all contracts for a specific expiration."""
        return [c for c in self.contracts if c.expiration == expiration]
    
    def get_contracts_by_strike(self, strike: float, option_type: OptionType) -> List[OptionContract]:
        """Get contracts by strike and type."""
        return [
            c for c in self.contracts 
            if c.strike == strike and c.option_type == option_type
        ]


class StrategyParameters(BaseModel):
    """Base strategy parameters."""
    symbol: str
    strategy_type: StrategyType
    quantity: int = 1  # Number of contracts/shares
    
    class Config:
        use_enum_values = True


class CoveredCallParams(StrategyParameters):
    """Covered Call strategy parameters."""
    strategy_type: StrategyType = StrategyType.COVERED_CALL
    stock_quantity: int = 100  # Number of shares
    call_strike: float
    call_expiration: str
    stock_price: Optional[float] = None  # If not provided, will fetch from market


class IronCondorParams(StrategyParameters):
    """Iron Condor strategy parameters."""
    strategy_type: StrategyType = StrategyType.IRON_CONDOR
    put_sell_strike: float
    put_buy_strike: float
    call_sell_strike: float
    call_buy_strike: float
    expiration: str
    quantity: int = 1  # Number of spreads


class ProfitPoint(BaseModel):
    """Profit/loss at a specific underlying price."""
    underlying_price: float
    profit_loss: float
    roi: float  # Return on investment as percentage


class BreakevenPoint(BaseModel):
    """Breakeven point information."""
    price: float
    direction: str  # "above" or "below"


class StrategyGreeks(BaseModel):
    """Greeks for a strategy."""
    delta: float
    gamma: float
    theta: float
    vega: float


class StrategyResult(BaseModel):
    """Strategy analysis result."""
    strategy_type: StrategyType
    symbol: str
    parameters: Dict[str, Any]
    entry_cost: float  # Negative for credit, positive for debit
    max_profit: float
    max_loss: float
    breakeven_points: List[BreakevenPoint]
    profit_profile: List[ProfitPoint]  # P&L at various price points
    greeks: Optional[StrategyGreeks] = None
    probability_of_profit: Optional[float] = None  # Based on delta
    risk_reward_ratio: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class FilterCriteria(BaseModel):
    """Filter criteria for strategy ranking."""
    min_profit: Optional[float] = None
    min_risk_reward: Optional[float] = None
    min_probability: Optional[float] = None
    max_loss: Optional[float] = None
    min_premium_collected: Optional[float] = None
    max_breakeven_range: Optional[float] = None
    symbol: Optional[str] = None
    strategy_type: Optional[StrategyType] = None
    
    class Config:
        use_enum_values = True


class StrategyRanking(BaseModel):
    """Ranked strategy result with score."""
    result: StrategyResult
    score: float
    ranking_metrics: Dict[str, float]


class AnalysisResponse(BaseModel):
    """Response model for strategy analysis."""
    results: List[StrategyResult]
    total_analyzed: int
    filtered_count: int


class OptionsChainResponse(BaseModel):
    """Response model for options chain."""
    chain: OptionsChain
    expirations: List[str]
    strikes: List[float]


