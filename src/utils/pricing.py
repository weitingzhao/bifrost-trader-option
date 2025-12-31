"""Options pricing utilities using py_vollib and QuantLib."""
import math
from typing import Optional
from datetime import datetime
import logging

try:
    from py_vollib.black_scholes import black_scholes
    from py_vollib.black_scholes.greeks.analytical import (
        delta, gamma, theta, vega
    )
    PY_VOLLIB_AVAILABLE = True
except ImportError:
    PY_VOLLIB_AVAILABLE = False
    logging.warning("py_vollib not available. Install with: pip install py_vollib")

try:
    import QuantLib as ql
    QUANTLIB_AVAILABLE = True
except ImportError:
    QUANTLIB_AVAILABLE = False
    logging.warning("QuantLib not available. Install with: conda install -c conda-forge quantlib-python")
    logging.warning("Or build from source. QuantLib-Python 1.31+ not available via pip.")

logger = logging.getLogger(__name__)


def calculate_black_scholes_price(
    underlying_price: float,
    strike: float,
    time_to_expiration: float,  # In years
    risk_free_rate: float,  # Annual risk-free rate (e.g., 0.05 for 5%)
    volatility: float,  # Annual volatility (e.g., 0.20 for 20%)
    option_type: str,  # 'CALL' or 'PUT'
    use_quantlib: bool = False
) -> Optional[float]:
    """
    Calculate option price using Black-Scholes model.
    
    Args:
        underlying_price: Current stock price
        strike: Strike price
        time_to_expiration: Time to expiration in years
        risk_free_rate: Annual risk-free interest rate
        volatility: Annual volatility (implied or historical)
        option_type: 'CALL' or 'PUT'
        use_quantlib: Use QuantLib instead of py_vollib
        
    Returns:
        Option price or None if calculation fails
    """
    if time_to_expiration <= 0:
        return 0.0
    
    try:
        if use_quantlib and QUANTLIB_AVAILABLE:
            return _quantlib_black_scholes(
                underlying_price, strike, time_to_expiration,
                risk_free_rate, volatility, option_type
            )
        elif PY_VOLLIB_AVAILABLE:
            flag = 'c' if option_type.upper() == 'CALL' else 'p'
            return black_scholes(
                flag, underlying_price, strike, time_to_expiration,
                risk_free_rate, volatility
            )
        else:
            logger.error("Neither py_vollib nor QuantLib is available")
            return None
    except Exception as e:
        logger.error(f"Error calculating Black-Scholes price: {e}")
        return None


def calculate_greeks(
    underlying_price: float,
    strike: float,
    time_to_expiration: float,
    risk_free_rate: float,
    volatility: float,
    option_type: str,
    use_quantlib: bool = False
) -> dict:
    """
    Calculate option Greeks (delta, gamma, theta, vega).
    
    Args:
        underlying_price: Current stock price
        strike: Strike price
        time_to_expiration: Time to expiration in years
        risk_free_rate: Annual risk-free interest rate
        volatility: Annual volatility
        option_type: 'CALL' or 'PUT'
        use_quantlib: Use QuantLib instead of py_vollib
        
    Returns:
        dict with delta, gamma, theta, vega
    """
    if time_to_expiration <= 0:
        return {'delta': 0.0, 'gamma': 0.0, 'theta': 0.0, 'vega': 0.0}
    
    try:
        if use_quantlib and QUANTLIB_AVAILABLE:
            return _quantlib_greeks(
                underlying_price, strike, time_to_expiration,
                risk_free_rate, volatility, option_type
            )
        elif PY_VOLLIB_AVAILABLE:
            flag = 'c' if option_type.upper() == 'CALL' else 'p'
            return {
                'delta': delta(flag, underlying_price, strike, time_to_expiration, risk_free_rate, volatility),
                'gamma': gamma(flag, underlying_price, strike, time_to_expiration, risk_free_rate, volatility),
                'theta': theta(flag, underlying_price, strike, time_to_expiration, risk_free_rate, volatility),
                'vega': vega(flag, underlying_price, strike, time_to_expiration, risk_free_rate, volatility),
            }
        else:
            logger.error("Neither py_vollib nor QuantLib is available")
            return {'delta': 0.0, 'gamma': 0.0, 'theta': 0.0, 'vega': 0.0}
    except Exception as e:
        logger.error(f"Error calculating Greeks: {e}")
        return {'delta': 0.0, 'gamma': 0.0, 'theta': 0.0, 'vega': 0.0}


def _quantlib_black_scholes(
    underlying_price: float,
    strike: float,
    time_to_expiration: float,
    risk_free_rate: float,
    volatility: float,
    option_type: str
) -> float:
    """Calculate Black-Scholes price using QuantLib."""
    # Set up QuantLib objects
    option_type_ql = ql.Option.Call if option_type.upper() == 'CALL' else ql.Option.Put
    
    # Create calendar and day counter
    calendar = ql.NullCalendar()
    day_count = ql.Actual365Fixed()
    
    # Set up dates
    today = ql.Date.todaysDate()
    expiration_date = today + int(time_to_expiration * 365)
    
    # Set up market data
    spot = ql.SimpleQuote(underlying_price)
    rate = ql.SimpleQuote(risk_free_rate)
    vol = ql.SimpleQuote(volatility)
    
    # Set up discount curve
    rate_ts = ql.FlatForward(today, ql.QuoteHandle(rate), day_count)
    vol_ts = ql.BlackConstantVol(today, calendar, ql.QuoteHandle(vol), day_count)
    
    # Create option
    payoff = ql.PlainVanillaPayoff(option_type_ql, strike)
    exercise = ql.EuropeanExercise(expiration_date)
    option = ql.VanillaOption(payoff, exercise)
    
    # Set up pricing engine
    bsm_process = ql.BlackScholesMertonProcess(
        ql.QuoteHandle(spot),
        ql.YieldTermStructureHandle(rate_ts),
        ql.BlackVolTermStructureHandle(vol_ts)
    )
    engine = ql.AnalyticEuropeanEngine(bsm_process)
    option.setPricingEngine(engine)
    
    return option.NPV()


def _quantlib_greeks(
    underlying_price: float,
    strike: float,
    time_to_expiration: float,
    risk_free_rate: float,
    volatility: float,
    option_type: str
) -> dict:
    """Calculate Greeks using QuantLib."""
    # Set up QuantLib objects (same as _quantlib_black_scholes)
    option_type_ql = ql.Option.Call if option_type.upper() == 'CALL' else ql.Option.Put
    
    calendar = ql.NullCalendar()
    day_count = ql.Actual365Fixed()
    today = ql.Date.todaysDate()
    expiration_date = today + int(time_to_expiration * 365)
    
    spot = ql.SimpleQuote(underlying_price)
    rate = ql.SimpleQuote(risk_free_rate)
    vol = ql.SimpleQuote(volatility)
    
    rate_ts = ql.FlatForward(today, ql.QuoteHandle(rate), day_count)
    vol_ts = ql.BlackConstantVol(today, calendar, ql.QuoteHandle(vol), day_count)
    
    payoff = ql.PlainVanillaPayoff(option_type_ql, strike)
    exercise = ql.EuropeanExercise(expiration_date)
    option = ql.VanillaOption(payoff, exercise)
    
    bsm_process = ql.BlackScholesMertonProcess(
        ql.QuoteHandle(spot),
        ql.YieldTermStructureHandle(rate_ts),
        ql.BlackVolTermStructureHandle(vol_ts)
    )
    engine = ql.AnalyticEuropeanEngine(bsm_process)
    option.setPricingEngine(engine)
    
    return {
        'delta': option.delta(),
        'gamma': option.gamma(),
        'theta': option.theta() / 365.0,  # Convert to per-day
        'vega': option.vega() / 100.0,  # Convert to per 1% vol change
    }


def calculate_implied_volatility(
    market_price: float,
    underlying_price: float,
    strike: float,
    time_to_expiration: float,
    risk_free_rate: float,
    option_type: str,
    use_quantlib: bool = False
) -> Optional[float]:
    """
    Calculate implied volatility from market price.
    
    Args:
        market_price: Current market price of the option
        underlying_price: Current stock price
        strike: Strike price
        time_to_expiration: Time to expiration in years
        risk_free_rate: Annual risk-free interest rate
        option_type: 'CALL' or 'PUT'
        use_quantlib: Use QuantLib instead of py_vollib
        
    Returns:
        Implied volatility or None if calculation fails
    """
    if time_to_expiration <= 0:
        return None
    
    try:
        if use_quantlib and QUANTLIB_AVAILABLE:
            return _quantlib_implied_volatility(
                market_price, underlying_price, strike,
                time_to_expiration, risk_free_rate, option_type
            )
        elif PY_VOLLIB_AVAILABLE:
            from py_vollib.black_scholes.implied_volatility import implied_volatility
            flag = 'c' if option_type.upper() == 'CALL' else 'p'
            return implied_volatility(
                market_price, underlying_price, strike,
                time_to_expiration, risk_free_rate, flag
            )
        else:
            logger.error("Neither py_vollib nor QuantLib is available")
            return None
    except Exception as e:
        logger.error(f"Error calculating implied volatility: {e}")
        return None


def _quantlib_implied_volatility(
    market_price: float,
    underlying_price: float,
    strike: float,
    time_to_expiration: float,
    risk_free_rate: float,
    option_type: str
) -> float:
    """Calculate implied volatility using QuantLib."""
    option_type_ql = ql.Option.Call if option_type.upper() == 'CALL' else ql.Option.Put
    
    calendar = ql.NullCalendar()
    day_count = ql.Actual365Fixed()
    today = ql.Date.todaysDate()
    expiration_date = today + int(time_to_expiration * 365)
    
    spot = ql.SimpleQuote(underlying_price)
    rate = ql.SimpleQuote(risk_free_rate)
    
    rate_ts = ql.FlatForward(today, ql.QuoteHandle(rate), day_count)
    
    payoff = ql.PlainVanillaPayoff(option_type_ql, strike)
    exercise = ql.EuropeanExercise(expiration_date)
    option = ql.VanillaOption(payoff, exercise)
    
    # Use bisection method to find implied volatility
    vol_guess = 0.20  # 20% initial guess
    vol = ql.SimpleQuote(vol_guess)
    vol_ts = ql.BlackConstantVol(today, calendar, ql.QuoteHandle(vol), day_count)
    
    bsm_process = ql.BlackScholesMertonProcess(
        ql.QuoteHandle(spot),
        ql.YieldTermStructureHandle(rate_ts),
        ql.BlackVolTermStructureHandle(vol_ts)
    )
    engine = ql.AnalyticEuropeanEngine(bsm_process)
    option.setPricingEngine(engine)
    
    # Use QuantLib's implied volatility solver
    try:
        implied_vol = option.impliedVolatility(market_price, bsm_process, 1e-4, 100, 0.0, 2.0)
        return implied_vol
    except Exception as e:
        logger.error(f"QuantLib implied volatility calculation failed: {e}")
        return None

