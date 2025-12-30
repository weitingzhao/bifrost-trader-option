"""Iron Condor strategy calculator."""
from typing import Optional, List

from .base_strategy import BaseStrategy
from ..models import (
    IronCondorParams, BreakevenPoint, StrategyGreeks,
    StrategyType, OptionContract, OptionType
)


class IronCondor(BaseStrategy):
    """
    Iron Condor strategy.
    
    Strategy: Sell put spread + Sell call spread
    - Sell lower strike put, buy even lower strike put
    - Sell lower strike call, buy higher strike call
    """
    
    def __init__(
        self,
        symbol: str,
        put_sell_contract: OptionContract,
        put_buy_contract: OptionContract,
        call_sell_contract: OptionContract,
        call_buy_contract: OptionContract,
        quantity: int = 1
    ):
        """
        Initialize Iron Condor strategy.
        
        Args:
            symbol: Stock symbol
            put_sell_contract: Put option to sell (higher strike)
            put_buy_contract: Put option to buy (lower strike)
            call_sell_contract: Call option to sell (lower strike)
            call_buy_contract: Call option to buy (higher strike)
            quantity: Number of spreads
        """
        super().__init__(symbol, StrategyType.IRON_CONDOR)
        self.put_sell_contract = put_sell_contract
        self.put_buy_contract = put_buy_contract
        self.call_sell_contract = call_sell_contract
        self.call_buy_contract = call_buy_contract
        self.quantity = quantity
        
        # Validate strikes
        if put_buy_contract.strike >= put_sell_contract.strike:
            raise ValueError("Put buy strike must be less than put sell strike")
        if call_sell_contract.strike >= call_buy_contract.strike:
            raise ValueError("Call sell strike must be less than call buy strike")
        if put_sell_contract.strike >= call_sell_contract.strike:
            raise ValueError("Put sell strike should be less than call sell strike")
    
    @classmethod
    def from_params(
        cls,
        params: IronCondorParams,
        put_sell_contract: OptionContract,
        put_buy_contract: OptionContract,
        call_sell_contract: OptionContract,
        call_buy_contract: OptionContract
    ) -> 'IronCondor':
        """
        Create IronCondor from parameters.
        
        Args:
            params: IronCondorParams
            put_sell_contract: Put option to sell
            put_buy_contract: Put option to buy
            call_sell_contract: Call option to sell
            call_buy_contract: Call option to buy
            
        Returns:
            IronCondor instance
        """
        return cls(
            symbol=params.symbol,
            put_sell_contract=put_sell_contract,
            put_buy_contract=put_buy_contract,
            call_sell_contract=call_sell_contract,
            call_buy_contract=call_buy_contract,
            quantity=params.quantity
        )
    
    def calculate_entry_cost(self) -> float:
        """
        Calculate entry cost (net credit/debit).
        
        Iron Condor: Premium received from selling - premium paid for buying
        Typically a credit strategy
        
        Returns:
            Entry cost (negative for credit, positive for debit)
        """
        # Premiums received (we're selling)
        put_sell_premium = self.put_sell_contract.bid * 100 * self.quantity
        call_sell_premium = self.call_sell_contract.bid * 100 * self.quantity
        
        # Premiums paid (we're buying)
        put_buy_premium = self.put_buy_contract.ask * 100 * self.quantity
        call_buy_premium = self.call_buy_contract.ask * 100 * self.quantity
        
        net_credit = (put_sell_premium + call_sell_premium) - (put_buy_premium + call_buy_premium)
        
        return -net_credit  # Negative for credit
    
    def calculate_profit_loss(self, underlying_price: float) -> float:
        """
        Calculate profit/loss at expiration for given underlying price.
        
        Args:
            underlying_price: Price of underlying at expiration
            
        Returns:
            Profit (positive) or loss (negative)
        """
        # Put spread P&L
        if underlying_price >= self.put_sell_contract.strike:
            # Both puts expire worthless
            put_pnl = (self.put_sell_contract.bid - self.put_buy_contract.ask) * 100 * self.quantity
        elif underlying_price <= self.put_buy_contract.strike:
            # Both puts are in-the-money, max loss
            put_pnl = -(self.put_sell_contract.strike - self.put_buy_contract.strike) * 100 * self.quantity
            put_pnl += (self.put_sell_contract.bid - self.put_buy_contract.ask) * 100 * self.quantity
        else:
            # Between strikes, partial loss
            put_pnl = -(self.put_sell_contract.strike - underlying_price) * 100 * self.quantity
            put_pnl += (self.put_sell_contract.bid - self.put_buy_contract.ask) * 100 * self.quantity
        
        # Call spread P&L
        if underlying_price <= self.call_sell_contract.strike:
            # Both calls expire worthless
            call_pnl = (self.call_sell_contract.bid - self.call_buy_contract.ask) * 100 * self.quantity
        elif underlying_price >= self.call_buy_contract.strike:
            # Both calls are in-the-money, max loss
            call_pnl = -(self.call_buy_contract.strike - self.call_sell_contract.strike) * 100 * self.quantity
            call_pnl += (self.call_sell_contract.bid - self.call_buy_contract.ask) * 100 * self.quantity
        else:
            # Between strikes, partial loss
            call_pnl = -(underlying_price - self.call_sell_contract.strike) * 100 * self.quantity
            call_pnl += (self.call_sell_contract.bid - self.call_buy_contract.ask) * 100 * self.quantity
        
        return put_pnl + call_pnl
    
    def calculate_max_profit(self) -> float:
        """
        Calculate maximum profit.
        
        Max profit occurs when stock price is between put_sell_strike and call_sell_strike.
        Profit = net credit received
        
        Returns:
            Maximum profit
        """
        net_credit = -self.calculate_entry_cost()  # Convert back to positive credit
        return net_credit
    
    def calculate_max_loss(self) -> float:
        """
        Calculate maximum loss.
        
        Max loss occurs if stock goes below put_buy_strike or above call_buy_strike.
        Loss = (put_spread_width + call_spread_width) - net_credit
        
        Returns:
            Maximum loss (positive value)
        """
        put_spread_width = (self.put_sell_contract.strike - self.put_buy_contract.strike) * 100 * self.quantity
        call_spread_width = (self.call_buy_contract.strike - self.call_sell_contract.strike) * 100 * self.quantity
        
        max_loss = put_spread_width + call_spread_width
        net_credit = -self.calculate_entry_cost()
        max_loss -= net_credit
        
        return max(max_loss, 0.0)
    
    def calculate_breakeven_points(self) -> List[BreakevenPoint]:
        """
        Calculate breakeven points.
        
        Lower breakeven = put_sell_strike - net_credit_per_share
        Upper breakeven = call_sell_strike + net_credit_per_share
        
        Returns:
            List of breakeven points
        """
        net_credit = -self.calculate_entry_cost()
        net_credit_per_share = net_credit / (100 * self.quantity)
        
        lower_breakeven = self.put_sell_contract.strike - net_credit_per_share
        upper_breakeven = self.call_sell_contract.strike + net_credit_per_share
        
        return [
            BreakevenPoint(price=round(lower_breakeven, 2), direction="below"),
            BreakevenPoint(price=round(upper_breakeven, 2), direction="above")
        ]
    
    def calculate_greeks(self) -> Optional[StrategyGreeks]:
        """
        Calculate strategy Greeks.
        
        Iron Condor Greeks (sum of all positions):
        - Delta: sum of all option deltas
        - Gamma: sum of all option gammas
        - Theta: sum of all option thetas (positive from short options)
        - Vega: sum of all option vegas (negative from short options)
        
        Returns:
            StrategyGreeks or None if contracts don't have Greeks
        """
        if (self.put_sell_contract.delta is None or 
            self.put_buy_contract.delta is None or
            self.call_sell_contract.delta is None or
            self.call_buy_contract.delta is None):
            return None
        
        # Put sell (short)
        put_sell_delta = -self.put_sell_contract.delta * 100 * self.quantity
        put_sell_gamma = -self.put_sell_contract.gamma * 100 * self.quantity if self.put_sell_contract.gamma else 0.0
        put_sell_theta = -self.put_sell_contract.theta * 100 * self.quantity if self.put_sell_contract.theta else 0.0
        put_sell_vega = -self.put_sell_contract.vega * 100 * self.quantity if self.put_sell_contract.vega else 0.0
        
        # Put buy (long)
        put_buy_delta = self.put_buy_contract.delta * 100 * self.quantity
        put_buy_gamma = self.put_buy_contract.gamma * 100 * self.quantity if self.put_buy_contract.gamma else 0.0
        put_buy_theta = self.put_buy_contract.theta * 100 * self.quantity if self.put_buy_contract.theta else 0.0
        put_buy_vega = self.put_buy_contract.vega * 100 * self.quantity if self.put_buy_contract.vega else 0.0
        
        # Call sell (short)
        call_sell_delta = -self.call_sell_contract.delta * 100 * self.quantity
        call_sell_gamma = -self.call_sell_contract.gamma * 100 * self.quantity if self.call_sell_contract.gamma else 0.0
        call_sell_theta = -self.call_sell_contract.theta * 100 * self.quantity if self.call_sell_contract.theta else 0.0
        call_sell_vega = -self.call_sell_contract.vega * 100 * self.quantity if self.call_sell_contract.vega else 0.0
        
        # Call buy (long)
        call_buy_delta = self.call_buy_contract.delta * 100 * self.quantity
        call_buy_gamma = self.call_buy_contract.gamma * 100 * self.quantity if self.call_buy_contract.gamma else 0.0
        call_buy_theta = self.call_buy_contract.theta * 100 * self.quantity if self.call_buy_contract.theta else 0.0
        call_buy_vega = self.call_buy_contract.vega * 100 * self.quantity if self.call_buy_contract.vega else 0.0
        
        return StrategyGreeks(
            delta=put_sell_delta + put_buy_delta + call_sell_delta + call_buy_delta,
            gamma=put_sell_gamma + put_buy_gamma + call_sell_gamma + call_buy_gamma,
            theta=put_sell_theta + put_buy_theta + call_sell_theta + call_buy_theta,
            vega=put_sell_vega + put_buy_vega + call_sell_vega + call_buy_vega
        )
    
    def _get_parameters(self) -> dict:
        """Get strategy parameters as dictionary."""
        return {
            "put_sell_strike": self.put_sell_contract.strike,
            "put_buy_strike": self.put_buy_contract.strike,
            "call_sell_strike": self.call_sell_contract.strike,
            "call_buy_strike": self.call_buy_contract.strike,
            "expiration": self.put_sell_contract.expiration,  # All should have same expiration
            "quantity": self.quantity,
            "put_sell_premium": self.put_sell_contract.bid,
            "put_buy_premium": self.put_buy_contract.ask,
            "call_sell_premium": self.call_sell_contract.bid,
            "call_buy_premium": self.call_buy_contract.ask
        }

