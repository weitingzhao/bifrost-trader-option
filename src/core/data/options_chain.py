"""Options chain data fetcher."""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

from ib_insync import Option as IBOption, Ticker

from ..connector.ib import get_connector
from .exchange import get_exchange_manager
from app_fastapi.database.schemas import OptionContract, OptionType, OptionsChain
from ...config import config

logger = logging.getLogger(__name__)


class OptionsChainFetcher:
    """Fetches and processes options chain data from IB."""

    def __init__(self):
        """Initialize the options chain fetcher."""
        self._cache: Dict[str, Tuple[OptionsChain, float]] = (
            {}
        )  # symbol -> (chain, timestamp)

    def _is_cache_valid(self, symbol: str) -> bool:
        """Check if cached data is still valid."""
        if symbol not in self._cache:
            return False

        _, timestamp = self._cache[symbol]
        age = datetime.now().timestamp() - timestamp
        return age < config.OPTIONS_CACHE_TTL

    def _get_from_cache(self, symbol: str) -> Optional[OptionsChain]:
        """Get options chain from cache if valid."""
        if self._is_cache_valid(symbol):
            chain, _ = self._cache[symbol]
            return chain
        return None

    def _update_cache(self, symbol: str, chain: OptionsChain):
        """Update cache with new chain data."""
        self._cache[symbol] = (chain, datetime.now().timestamp())

    async def fetch_chain(
        self, symbol: str, exchange: Optional[str] = None, use_cache: bool = True
    ) -> Optional[OptionsChain]:
        """
        Fetch options chain for a symbol.

        Args:
            symbol: Stock symbol
            exchange: Optional exchange specification (auto-detected if not provided)
            use_cache: Whether to use cached data if available

        Returns:
            OptionsChain or None if error
        """
        # Check cache first
        if use_cache:
            cached = self._get_from_cache(symbol)
            if cached:
                logger.debug(f"Using cached options chain for {symbol}")
                return cached

        try:
            connector = await get_connector()
            exchange_manager = get_exchange_manager()

            # Detect exchange if not provided
            if exchange is None:
                exchange = await exchange_manager.detect_stock_exchange(symbol)

            # Get underlying stock price with exchange
            underlying_price = await connector.get_stock_price(symbol, exchange)
            if underlying_price is None:
                logger.warning(f"Could not get stock price for {symbol}")
                underlying_price = 0.0

            # Get option exchange (OPRA for US options)
            option_exchange = exchange_manager.get_option_exchange(symbol)

            # Get option chain contract details with exchange
            contract_details_list = await connector.get_option_chain(symbol, exchange)

            if not contract_details_list:
                logger.warning(f"No option contracts found for {symbol}")
                return None

            # Convert to our model
            contracts: List[OptionContract] = []

            # Process contracts in batches to get market data
            batch_size = 50
            for i in range(0, len(contract_details_list), batch_size):
                batch = contract_details_list[i : i + batch_size]

                # Get market data for batch
                tickers = await self._get_tickers_batch(batch)

                for details, ticker in zip(batch, tickers):
                    if ticker is None:
                        continue

                    contract = details.contract
                    if not isinstance(contract, IBOption):
                        continue

                    # Parse expiration (IB format: YYYYMMDD)
                    expiration = contract.lastTradeDateOrContractMonth

                    # Determine option type
                    option_type = (
                        OptionType.CALL if contract.right == "C" else OptionType.PUT
                    )

                    # Get bid/ask
                    bid = ticker.bid if ticker.bid and ticker.bid > 0 else 0.0
                    ask = ticker.ask if ticker.ask and ticker.ask > 0 else 0.0
                    mid = (
                        (bid + ask) / 2
                        if bid > 0 and ask > 0
                        else (ticker.close if ticker.close else 0.0)
                    )

                    # Get Greeks from model option computation
                    delta = ticker.modelGreeks.delta if ticker.modelGreeks else None
                    gamma = ticker.modelGreeks.gamma if ticker.modelGreeks else None
                    theta = ticker.modelGreeks.theta if ticker.modelGreeks else None
                    vega = ticker.modelGreeks.vega if ticker.modelGreeks else None

                    # Get IV
                    iv = (
                        ticker.modelGreeks.impliedVolatility
                        if ticker.modelGreeks
                        else None
                    )

                    # Get exchange from contract or use detected option exchange
                    contract_exchange = (
                        getattr(contract, "exchange", None) or option_exchange
                    )

                    option_contract = OptionContract(
                        symbol=symbol,
                        strike=contract.strike,
                        expiration=expiration,
                        option_type=option_type,
                        bid=bid,
                        ask=ask,
                        last=mid,
                        volume=ticker.volume if ticker.volume else 0,
                        open_interest=(
                            details.contract.openInterest
                            if hasattr(details.contract, "openInterest")
                            else 0
                        ),
                        implied_volatility=iv,
                        delta=delta,
                        gamma=gamma,
                        theta=theta,
                        vega=vega,
                        contract_id=contract.conId,
                        exchange=contract_exchange,
                    )

                    contracts.append(option_contract)

                # Small delay between batches to avoid rate limiting
                if i + batch_size < len(contract_details_list):
                    await asyncio.sleep(0.1)

            if not contracts:
                logger.warning(f"No valid option contracts found for {symbol}")
                return None

            # Create options chain
            chain = OptionsChain(
                symbol=symbol, underlying_price=underlying_price, contracts=contracts
            )

            # Update cache
            self._update_cache(symbol, chain)

            logger.info(f"Fetched {len(contracts)} option contracts for {symbol}")
            return chain

        except Exception as e:
            logger.error(f"Error fetching options chain for {symbol}: {e}")
            return None

    async def fetch_options_chain_full(
        self, symbol: str, exchange: Optional[str] = None, use_cache: bool = False
    ) -> Optional[OptionsChain]:
        """
        Fetch full options chain (all strikes, all expirations) with exchange support.

        Args:
            symbol: Stock symbol
            exchange: Optional exchange specification (auto-detected if not provided)
            use_cache: Whether to use cached data (defaults to False for full chain)

        Returns:
            OptionsChain or None if error
        """
        return await self.fetch_chain(symbol, exchange, use_cache)

    async def _get_tickers_batch(
        self, contract_details_list: List
    ) -> List[Optional[Ticker]]:
        """Get tickers for a batch of contracts."""
        connector = await get_connector()
        tickers = []

        for details in contract_details_list:
            contract = details.contract
            try:
                ticker = await connector.get_option_ticker(contract)
                tickers.append(ticker)
            except Exception as e:
                logger.debug(f"Error getting ticker for {contract}: {e}")
                tickers.append(None)

        return tickers

    def clear_cache(self, symbol: Optional[str] = None):
        """
        Clear cache for a symbol or all symbols.

        Args:
            symbol: Symbol to clear cache for, or None to clear all
        """
        if symbol:
            self._cache.pop(symbol, None)
        else:
            self._cache.clear()


# Global fetcher instance
_fetcher: Optional[OptionsChainFetcher] = None


async def get_fetcher() -> OptionsChainFetcher:
    """Get or create the global options chain fetcher instance."""
    global _fetcher
    if _fetcher is None:
        _fetcher = OptionsChainFetcher()
    return _fetcher
