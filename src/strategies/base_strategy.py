"""Base strategy class with common P&L calculation methods."""
from abc import ABC, abstractmethod
from typing import List, Optional
import math

from app_fastapi.database.schemas import (
    StrategyResult, ProfitPoint, BreakevenPoint, StrategyGreeks,
    StrategyType
)


class BaseStrategy(ABC):
    """Base class for all option strategies."""
    
    def __init__(self, symbol: str, strategy_type: StrategyType):
        """
        Initialize base strategy.
        
        Args:
            symbol: Stock symbol
            strategy_type: Type of strategy
        """
        self.symbol = symbol
        self.strategy_type = strategy_type
    
    @abstractmethod
    def calculate_entry_cost(self) -> float:
        """
        Calculate the entry cost (negative for credit, positive for debit).
        
        Returns:
            Entry cost
        """
        pass
    
    @abstractmethod
    def calculate_profit_loss(self, underlying_price: float) -> float:
        """
        Calculate profit/loss at a given underlying price.
        
        Args:
            underlying_price: Price of underlying at expiration
            
        Returns:
            Profit (positive) or loss (negative)
        """
        pass
    
    @abstractmethod
    def calculate_max_profit(self) -> float:
        """
        Calculate maximum profit.
        
        Returns:
            Maximum profit
        """
        pass
    
    @abstractmethod
    def calculate_max_loss(self) -> float:
        """
        Calculate maximum loss.
        
        Returns:
            Maximum loss (positive value)
        """
        pass
    
    @abstractmethod
    def calculate_breakeven_points(self) -> List[BreakevenPoint]:
        """
        Calculate breakeven points.
        
        Returns:
            List of breakeven points
        """
        pass
    
    @abstractmethod
    def calculate_greeks(self) -> Optional[StrategyGreeks]:
        """
        Calculate strategy Greeks.
        
        Returns:
            StrategyGreeks or None if not available
        """
        pass
    
    def generate_profit_profile(
        self,
        min_price: float,
        max_price: float,
        num_points: int = 100
    ) -> List[ProfitPoint]:
        """
        Generate profit profile across a range of underlying prices.
        
        Args:
            min_price: Minimum underlying price
            max_price: Maximum underlying price
            num_points: Number of points to calculate
            
        Returns:
            List of profit points
        """
        profile = []
        price_step = (max_price - min_price) / num_points
        
        entry_cost = self.calculate_entry_cost()
        
        for i in range(num_points + 1):
            price = min_price + (i * price_step)
            profit_loss = self.calculate_profit_loss(price)
            
            # Calculate ROI
            roi = (profit_loss / abs(entry_cost) * 100) if entry_cost != 0 else 0.0
            
            profile.append(ProfitPoint(
                underlying_price=round(price, 2),
                profit_loss=round(profit_loss, 2),
                roi=round(roi, 2)
            ))
        
        return profile
    
    def calculate_risk_reward_ratio(self) -> Optional[float]:
        """
        Calculate risk/reward ratio.
        
        Returns:
            Risk/reward ratio (max_profit / max_loss) or None if max_loss is 0
        """
        max_profit = self.calculate_max_profit()
        max_loss = self.calculate_max_loss()
        
        if max_loss == 0:
            return None
        
        return max_profit / max_loss
    
    def calculate_probability_of_profit(self) -> Optional[float]:
        """
        Calculate probability of profit based on delta.
        
        This is a simplified calculation. In practice, you'd use
        more sophisticated methods like Monte Carlo simulation.
        
        Returns:
            Probability of profit (0-1) or None if not calculable
        """
        greeks = self.calculate_greeks()
        if greeks is None or greeks.delta is None:
            return None
        
        # Simplified: use delta as rough proxy for probability
        # For long positions, higher delta = higher probability
        # This is a rough approximation
        delta = abs(greeks.delta)
        return min(max(delta, 0.0), 1.0)
    
    def analyze(self) -> StrategyResult:
        """
        Perform complete strategy analysis.
        
        Returns:
            StrategyResult with all calculated metrics
        """
        entry_cost = self.calculate_entry_cost()
        max_profit = self.calculate_max_profit()
        max_loss = self.calculate_max_loss()
        breakeven_points = self.calculate_breakeven_points()
        greeks = self.calculate_greeks()
        
        # Generate profit profile
        # Use a range around current price (if available) or reasonable range
        # For now, use a wide range - strategies can override
        min_price = 0.0
        max_price = 500.0
        profit_profile = self.generate_profit_profile(min_price, max_price)
        
        # Calculate additional metrics
        risk_reward = self.calculate_risk_reward_ratio()
        prob_of_profit = self.calculate_probability_of_profit()
        
        return StrategyResult(
            strategy_type=self.strategy_type,
            symbol=self.symbol,
            parameters=self._get_parameters(),
            entry_cost=round(entry_cost, 2),
            max_profit=round(max_profit, 2),
            max_loss=round(max_loss, 2),
            breakeven_points=breakeven_points,
            profit_profile=profit_profile,
            greeks=greeks,
            probability_of_profit=round(prob_of_profit, 4) if prob_of_profit else None,
            risk_reward_ratio=round(risk_reward, 4) if risk_reward else None
        )
    
    @abstractmethod
    def _get_parameters(self) -> dict:
        """
        Get strategy parameters as dictionary.
        
        Returns:
            Dictionary of parameters
        """
        pass


