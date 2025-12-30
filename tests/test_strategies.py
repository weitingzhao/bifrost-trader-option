"""Basic tests for strategy calculations."""
import pytest
from src.models import OptionContract, OptionType, StrategyType
from src.strategies import CoveredCall, IronCondor


def test_covered_call_calculation():
    """Test basic covered call calculation."""
    # Create a mock call contract
    call_contract = OptionContract(
        symbol="AAPL",
        strike=155.0,
        expiration="20240119",
        option_type=OptionType.CALL,
        bid=2.50,
        ask=2.60,
        delta=0.3,
        gamma=0.02,
        theta=-0.05,
        vega=0.15
    )
    
    # Create covered call strategy
    strategy = CoveredCall(
        symbol="AAPL",
        stock_price=150.0,
        stock_quantity=100,
        call_contract=call_contract,
        call_quantity=1
    )
    
    # Test calculations
    entry_cost = strategy.calculate_entry_cost()
    assert entry_cost > 0  # Should be a debit (buying stock)
    
    max_profit = strategy.calculate_max_profit()
    assert max_profit > 0
    
    # Test P&L at expiration
    pnl_at_strike = strategy.calculate_profit_loss(155.0)
    assert pnl_at_strike > 0  # Should be profitable at strike


def test_iron_condor_calculation():
    """Test basic iron condor calculation."""
    # Create mock contracts
    put_sell = OptionContract(
        symbol="AAPL",
        strike=145.0,
        expiration="20240119",
        option_type=OptionType.PUT,
        bid=2.00,
        ask=2.10,
        delta=-0.2,
        gamma=0.02,
        theta=-0.04,
        vega=0.12
    )
    
    put_buy = OptionContract(
        symbol="AAPL",
        strike=140.0,
        expiration="20240119",
        option_type=OptionType.PUT,
        bid=1.00,
        ask=1.10,
        delta=-0.1,
        gamma=0.01,
        theta=-0.02,
        vega=0.06
    )
    
    call_sell = OptionContract(
        symbol="AAPL",
        strike=155.0,
        expiration="20240119",
        option_type=OptionType.CALL,
        bid=2.00,
        ask=2.10,
        delta=0.2,
        gamma=0.02,
        theta=-0.04,
        vega=0.12
    )
    
    call_buy = OptionContract(
        symbol="AAPL",
        strike=160.0,
        expiration="20240119",
        option_type=OptionType.CALL,
        bid=1.00,
        ask=1.10,
        delta=0.1,
        gamma=0.01,
        theta=-0.02,
        vega=0.06
    )
    
    # Create iron condor strategy
    strategy = IronCondor(
        symbol="AAPL",
        put_sell_contract=put_sell,
        put_buy_contract=put_buy,
        call_sell_contract=call_sell,
        call_buy_contract=call_buy,
        quantity=1
    )
    
    # Test calculations
    entry_cost = strategy.calculate_entry_cost()
    assert entry_cost < 0  # Should be a credit (selling spreads)
    
    max_profit = strategy.calculate_max_profit()
    assert max_profit > 0
    
    # Test P&L at middle price (should be max profit)
    pnl_at_middle = strategy.calculate_profit_loss(150.0)
    assert pnl_at_middle > 0  # Should be profitable in the middle


