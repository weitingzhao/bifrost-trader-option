"""Exchange detection and routing manager for Interactive Brokers."""
import logging
from typing import Optional, Dict
from ib_insync import Stock, ContractDetails

from ...config import config
from ..connector.ib import get_connector

logger = logging.getLogger(__name__)


class ExchangeManager:
    """Manages exchange detection and routing for symbols."""
    
    def __init__(self):
        """Initialize the exchange manager."""
        # Cache for exchange mappings (symbol -> exchange)
        self._exchange_cache: Dict[str, str] = {}
        
        # Known exchange patterns (fallback when IB query fails)
        self._known_exchanges: Dict[str, str] = {
            # NASDAQ symbols (typically 4-5 letters)
            'AAPL': 'NASDAQ',
            'MSFT': 'NASDAQ',
            'GOOGL': 'NASDAQ',
            'AMZN': 'NASDAQ',
            'TSLA': 'NASDAQ',
            'META': 'NASDAQ',
            'NVDA': 'NASDAQ',
            'NFLX': 'NASDAQ',
            # NYSE symbols (typically 1-3 letters)
            'JPM': 'NYSE',
            'BAC': 'NYSE',
            'WMT': 'NYSE',
            'V': 'NYSE',
            'JNJ': 'NYSE',
            'PG': 'NYSE',
            'MA': 'NYSE',
            'HD': 'NYSE',
        }
    
    async def detect_stock_exchange(self, symbol: str) -> str:
        """
        Detect primary exchange for a stock symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'JPM')
            
        Returns:
            Exchange name ('NYSE', 'NASDAQ', 'NYSEAMERICAN', or 'SMART' as fallback)
        """
        symbol = symbol.upper()
        
        # Check cache first
        if symbol in self._exchange_cache:
            return self._exchange_cache[symbol]
        
        # Check configuration overrides
        if hasattr(config, 'IB_EXCHANGE_MAPPINGS') and symbol in config.IB_EXCHANGE_MAPPINGS:
            exchange = config.IB_EXCHANGE_MAPPINGS[symbol]
            self._exchange_cache[symbol] = exchange
            return exchange
        
        # Check known exchanges
        if symbol in self._known_exchanges:
            exchange = self._known_exchanges[symbol]
            self._exchange_cache[symbol] = exchange
            return exchange
        
        # Primary method: Query IB for contract details
        try:
            connector = await get_connector()
            if not connector.is_connected():
                await connector.connect()
            
            stock = Stock(symbol, 'SMART', 'USD')
            import asyncio
            loop = asyncio.get_event_loop()
            details = await loop.run_in_executor(
                None,
                lambda: connector.ib.reqContractDetails(stock)
            )
            
            if details and len(details) > 0:
                primary_exchange = details[0].contract.primaryExchange
                if primary_exchange:
                    # Normalize exchange names
                    exchange = self._normalize_exchange(primary_exchange)
                    self._exchange_cache[symbol] = exchange
                    logger.info(f"Detected exchange for {symbol}: {exchange}")
                    return exchange
        except Exception as e:
            logger.warning(f"Could not detect exchange for {symbol} via IB: {e}")
        
        # Fallback: Use symbol pattern
        exchange = self._detect_by_pattern(symbol)
        self._exchange_cache[symbol] = exchange
        logger.info(f"Using pattern-based detection for {symbol}: {exchange}")
        return exchange
    
    def _normalize_exchange(self, exchange: str) -> str:
        """
        Normalize IB exchange names to standard format.
        
        Args:
            exchange: IB exchange name
            
        Returns:
            Normalized exchange name
        """
        exchange = exchange.upper()
        
        # Map IB exchange names to standard names
        exchange_map = {
            'NYSE': 'NYSE',
            'NASDAQ': 'NASDAQ',
            'NASDAQOM': 'NASDAQ',
            'NASDAQOMX': 'NASDAQ',
            'AMEX': 'NYSEAMERICAN',
            'NYSEAMERICAN': 'NYSEAMERICAN',
            'NYSE ARCA': 'NYSE',
            'ARCA': 'NYSE',
        }
        
        return exchange_map.get(exchange, exchange)
    
    def _detect_by_pattern(self, symbol: str) -> str:
        """
        Detect exchange based on symbol pattern (fallback method).
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Detected exchange or 'SMART' as default
        """
        # NASDAQ: Typically 4-5 uppercase letters, no special characters
        if len(symbol) >= 4 and len(symbol) <= 5 and symbol.isalpha():
            return 'NASDAQ'
        
        # NYSE: Typically 1-3 letters, may include dots
        if len(symbol) <= 3:
            return 'NYSE'
        
        # Default to SMART routing
        return config.IB_DEFAULT_STOCK_EXCHANGE if hasattr(config, 'IB_DEFAULT_STOCK_EXCHANGE') else 'SMART'
    
    def get_option_exchange(self, underlying_symbol: str) -> str:
        """
        Get options exchange for a symbol.
        
        For US options, use OPRA (Options Price Reporting Authority).
        For international options, use SMART routing.
        
        Args:
            underlying_symbol: Underlying stock symbol
            
        Returns:
            Exchange name ('OPRA' for US options, 'SMART' for others)
        """
        # For US stocks, use OPRA for options
        # OPRA aggregates data from all US options exchanges
        underlying_symbol = underlying_symbol.upper()
        
        # Check if it's a US symbol (basic check)
        # In practice, most US-listed stocks will use OPRA
        if underlying_symbol.isalpha() and len(underlying_symbol) <= 5:
            return config.IB_DEFAULT_OPTION_EXCHANGE if hasattr(config, 'IB_DEFAULT_OPTION_EXCHANGE') else 'OPRA'
        
        # For international or unclear cases, use SMART
        return 'SMART'
    
    def is_nasdaq_symbol(self, symbol: str) -> bool:
        """Check if symbol is likely NASDAQ-listed."""
        exchange = self._exchange_cache.get(symbol.upper())
        if exchange:
            return exchange == 'NASDAQ'
        return self._detect_by_pattern(symbol.upper()) == 'NASDAQ'
    
    def is_nyse_symbol(self, symbol: str) -> bool:
        """Check if symbol is likely NYSE-listed."""
        exchange = self._exchange_cache.get(symbol.upper())
        if exchange:
            return exchange == 'NYSE'
        return self._detect_by_pattern(symbol.upper()) == 'NYSE'
    
    def is_nyse_american_symbol(self, symbol: str) -> bool:
        """Check if symbol is likely NYSE American-listed."""
        exchange = self._exchange_cache.get(symbol.upper())
        if exchange:
            return exchange == 'NYSEAMERICAN'
        return False
    
    def clear_cache(self, symbol: Optional[str] = None):
        """
        Clear exchange cache.
        
        Args:
            symbol: Symbol to clear, or None to clear all
        """
        if symbol:
            self._exchange_cache.pop(symbol.upper(), None)
        else:
            self._exchange_cache.clear()


# Global exchange manager instance
_exchange_manager: Optional[ExchangeManager] = None


def get_exchange_manager() -> ExchangeManager:
    """Get or create the global exchange manager instance."""
    global _exchange_manager
    if _exchange_manager is None:
        _exchange_manager = ExchangeManager()
    return _exchange_manager

