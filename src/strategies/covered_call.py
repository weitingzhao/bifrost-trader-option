"""Covered Call strategy calculator."""
from typing import Optional, List

from .base_strategy import BaseStrategy
from app_fastapi.database.schemas import (
    CoveredCallParams, BreakevenPoint, StrategyGreeks,
    StrategyType, OptionContract, OptionType
)


class CoveredCall(BaseStrategy):
    """
    Covered Call strategy.
    
    Strategy: Long stock + Short call option
    """
    
    def __init__(
        self,
        symbol: str,
        stock_price: float,
        stock_quantity: int,
        call_contract: OptionContract,
        call_quantity: int = 1
    ):
        """
        Initialize Covered Call strategy.
        
        Args:
            symbol: Stock symbol
            stock_price: Current stock price (entry price)
            stock_quantity: Number of shares (typically 100 per contract)
            call_contract: Call option contract to sell
            call_quantity: Number of call contracts to sell
        """
        super().__init__(symbol, StrategyType.COVERED_CALL)
        self.stock_price = stock_price
        self.stock_quantity = stock_quantity
        self.call_contract = call_contract
        self.call_quantity = call_quantity
        self.call_strike = call_contract.strike
        self.call_premium = call_contract.bid  # Premium received (use bid as we're selling)
    
    @classmethod
    def from_params(
        cls,
        params: CoveredCallParams,
        call_contract: OptionContract,
        stock_price: Optional[float] = None
    ) -> 'CoveredCall':
        """
        Create CoveredCall from parameters.
        
        Args:
            params: CoveredCallParams
            call_contract: Call option contract
            stock_price: Current stock price (if not in params)
            
        Returns:
            CoveredCall instance
        """
        stock_price = stock_price or params.stock_price
        if stock_price is None:
            raise ValueError("Stock price must be provided")
        
        return cls(
            symbol=params.symbol,
            stock_price=stock_price,
            stock_quantity=params.stock_quantity,
            call_contract=call_contract,
            call_quantity=params.quantity
        )
    
    def calculate_entry_cost(self) -> float:
        """
        Calculate entry cost.
        
        Covered Call: Cost of stock - premium received
        Returns negative value (net credit) if premium > 0
        
        Returns:
            Entry cost (negative for credit, positive for debit)
        """
        stock_cost = self.stock_price * self.stock_quantity
        premium_received = self.call_premium * 100 * self.call_quantity  # Options are per 100 shares
        return stock_cost - premium_received
    
    def calculate_profit_loss(self, underlying_price: float) -> float:
        """
        Calculate profit/loss at expiration for given underlying price.
        
        Args:
            underlying_price: Price of underlying at expiration
            
        Returns:
            Profit (positive) or loss (negative)
        """
        # Stock P&L
        stock_pnl = (underlying_price - self.stock_price) * self.stock_quantity
        
        # Call option P&L (we sold the call)
        if underlying_price <= self.call_strike:
            # Call expires worthless, we keep full premium
            call_pnl = self.call_premium * 100 * self.call_quantity
        else:
            # Call is exercised, we lose (price - strike) per share
            call_pnl = self.call_premium * 100 * self.call_quantity
            call_pnl -= (underlying_price - self.call_strike) * 100 * self.call_quantity
        
        return stock_pnl + call_pnl
    
    def calculate_max_profit(self) -> float:
        """
        Calculate maximum profit.
        
        Max profit occurs when stock price >= call strike at expiration.
        Profit = (strike - stock_price) * shares + premium received
        
        Returns:
            Maximum profit
        """
        if self.call_strike >= self.stock_price:
            # Out-of-the-money or at-the-money call
            max_profit = (self.call_strike - self.stock_price) * self.stock_quantity
            max_profit += self.call_premium * 100 * self.call_quantity
        else:
            # In-the-money call (less common for covered calls)
            max_profit = self.call_premium * 100 * self.call_quantity
        
        return max_profit
    
    def calculate_max_loss(self) -> float:
        """
        Calculate maximum loss.
        
        Max loss occurs if stock goes to zero.
        Loss = stock_price * shares - premium received
        
        Returns:
            Maximum loss (positive value)
        """
        stock_cost = self.stock_price * self.stock_quantity
        premium_received = self.call_premium * 100 * self.call_quantity
        max_loss = stock_cost - premium_received
        
        return max(max_loss, 0.0)  # Return as positive value
    
    def calculate_breakeven_points(self) -> List[BreakevenPoint]:
        """
        Calculate breakeven points.
        
        Breakeven = stock_price - (premium_per_share)
        
        Returns:
            List of breakeven points
        """
        premium_per_share = (self.call_premium * 100 * self.call_quantity) / self.stock_quantity
        breakeven = self.stock_price - premium_per_share
        
        return [BreakevenPoint(
            price=round(breakeven, 2),
            direction="below"
        )]
    
    def calculate_greeks(self) -> Optional[StrategyGreeks]:
        """
        Calculate strategy Greeks.
        
        Covered Call Greeks:
        - Delta: 1 (stock) - call_delta * 100 * quantity
        - Gamma: -call_gamma * 100 * quantity
        - Theta: -call_theta * 100 * quantity (positive theta from short call)
        - Vega: -call_vega * 100 * quantity
        
        Returns:
            StrategyGreeks or None if call contract doesn't have Greeks
        """
        if self.call_contract.delta is None:
            return None
        
        # Stock has delta = 1, gamma = 0, theta = 0, vega = 0
        stock_delta = 1.0 * self.stock_quantity
        
        # Call option Greeks (we're short)
        call_delta = -self.call_contract.delta * 100 * self.call_quantity
        call_gamma = -self.call_contract.gamma * 100 * self.call_quantity if self.call_contract.gamma else 0.0
        call_theta = -self.call_contract.theta * 100 * self.call_quantity if self.call_contract.theta else 0.0
        call_vega = -self.call_contract.vega * 100 * self.call_quantity if self.call_contract.vega else 0.0
        
        return StrategyGreeks(
            delta=stock_delta + call_delta,
            gamma=call_gamma,
            theta=call_theta,
            vega=call_vega
        )
    
    def _get_parameters(self) -> dict:
        """Get strategy parameters as dictionary."""
        return {
            "stock_price": self.stock_price,
            "stock_quantity": self.stock_quantity,
            "call_strike": self.call_strike,
            "call_expiration": self.call_contract.expiration,
            "call_premium": self.call_premium,
            "call_quantity": self.call_quantity
        }

