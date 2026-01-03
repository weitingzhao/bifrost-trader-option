"""Interactive Brokers connection manager."""

import asyncio
import logging
from typing import Optional, List
from ib_insync import IB, Stock, Option, Contract, util, Ticker, ContractDetails

from ...config import config

logger = logging.getLogger(__name__)


class IBConnector:
    """Manages connection to Interactive Brokers TWS/Gateway."""

    def __init__(self):
        """Initialize the IB connector."""
        self.ib = IB()
        self.connected = False
        self._connection_lock = asyncio.Lock()

    async def connect(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        client_id: Optional[int] = None,
    ) -> bool:
        """
        Connect to IB TWS/Gateway.

        Args:
            host: IB host (defaults to config)
            port: IB port (defaults to config)
            client_id: Client ID (defaults to config)

        Returns:
            True if connected successfully, False otherwise
        """
        async with self._connection_lock:
            if self.connected:
                logger.info("Already connected to IB")
                return True

            host = host or config.IB_HOST
            port = port or config.IB_PORT
            client_id = client_id or config.IB_CLIENT_ID

            try:
                # ib_insync uses asyncio, so we need to run in executor
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None, lambda: self.ib.connect(host, port, clientId=client_id)
                )
                self.connected = True
                logger.info(
                    f"Connected to IB at {host}:{port} with client ID {client_id}"
                )
                return True
            except Exception as e:
                logger.error(f"Failed to connect to IB: {e}")
                self.connected = False
                return False

    async def disconnect(self):
        """Disconnect from IB."""
        async with self._connection_lock:
            if not self.connected:
                return

            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.ib.disconnect)
                self.connected = False
                logger.info("Disconnected from IB")
            except Exception as e:
                logger.error(f"Error disconnecting from IB: {e}")

    def is_connected(self) -> bool:
        """Check if connected to IB."""
        return self.connected and self.ib.isConnected()

    async def get_stock_price(
        self, symbol: str, exchange: Optional[str] = None
    ) -> Optional[float]:
        """
        Get current stock price.

        Args:
            symbol: Stock symbol
            exchange: Optional exchange specification (defaults to SMART routing)

        Returns:
            Current stock price or None if error
        """
        if not self.is_connected():
            await self.connect()

        try:
            exchange = exchange or "SMART"
            stock = Stock(symbol, exchange, "USD")
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(
                None, lambda: self.ib.reqMktData(stock, "", False, False)
            )

            # Wait for ticker to update
            await asyncio.sleep(0.5)

            if ticker and ticker.marketPrice():
                return ticker.marketPrice()
            elif ticker and ticker.close:
                return ticker.close

            # Cancel market data
            self.ib.cancelMktData(stock)
            return None
        except Exception as e:
            logger.error(f"Error getting stock price for {symbol}: {e}")
            return None

    async def get_option_chain(
        self,
        symbol: str,
        exchange: Optional[str] = None,
        max_expirations: Optional[int] = None,
    ) -> List[ContractDetails]:
        """
        Get option chain contract details for a symbol.

        Args:
            symbol: Stock symbol
            exchange: Optional exchange specification for underlying (defaults to SMART)
            max_expirations: Optional limit on number of expirations (None = all)

        Returns:
            List of option contract details
        """
        if not self.is_connected():
            await self.connect()

        try:
            exchange = exchange or "SMART"
            stock = Stock(symbol, exchange, "USD")
            loop = asyncio.get_event_loop()

            # Request option chain
            chains = await loop.run_in_executor(
                None,
                lambda: self.ib.reqSecDefOptParams(
                    stock.symbol, "", stock.secType, stock.conId
                ),
            )

            if not chains:
                logger.warning(f"No option chains found for {symbol}")
                return []

            # Get the first chain (usually the most liquid)
            chain = chains[0]
            if not chain.expirations or not chain.strikes:
                logger.warning(f"Empty option chain for {symbol}")
                return []

            # Build contracts for all strikes and expirations (no limit)
            contracts = []
            expirations = (
                chain.expirations[:max_expirations]
                if max_expirations
                else chain.expirations
            )

            for exp in expirations:
                for strike in chain.strikes:
                    for right in ["C", "P"]:
                        # Use OPRA for US options, SMART for others
                        option_exchange = (
                            "OPRA"
                            if exchange in ["SMART", "NYSE", "NASDAQ", "NYSEAMERICAN"]
                            else "SMART"
                        )
                        option = Option(symbol, exp, strike, right, option_exchange)
                        contracts.append(option)

            # Request contract details in batches
            contract_details_list = []
            batch_size = (
                config.IB_COLLECTION_BATCH_SIZE
                if hasattr(config, "IB_COLLECTION_BATCH_SIZE")
                else 50
            )
            batch_delay = (
                config.IB_COLLECTION_BATCH_DELAY
                if hasattr(config, "IB_COLLECTION_BATCH_DELAY")
                else 0.1
            )

            for i in range(0, len(contracts), batch_size):
                batch = contracts[i : i + batch_size]

                for contract in batch:
                    try:
                        details = await loop.run_in_executor(
                            None, lambda c=contract: self.ib.reqContractDetails(c)
                        )
                        if details:
                            contract_details_list.extend(details)
                    except Exception as e:
                        logger.debug(f"Error getting details for {contract}: {e}")
                        continue

                # Rate limiting between batches
                if i + batch_size < len(contracts):
                    await asyncio.sleep(batch_delay)

            logger.info(
                f"Retrieved {len(contract_details_list)} option contracts for {symbol} (from {len(contracts)} requested)"
            )
            return contract_details_list
        except Exception as e:
            logger.error(f"Error getting option chain for {symbol}: {e}")
            return []

    async def get_option_chain_full(
        self,
        symbol: str,
        exchange: Optional[str] = None,
        max_expirations: Optional[int] = None,
    ) -> List[ContractDetails]:
        """
        Get full option chain (all strikes, all expirations) with exchange support.

        This is an alias for get_option_chain() with no limits.

        Args:
            symbol: Stock symbol
            exchange: Optional exchange specification
            max_expirations: Optional limit on expirations (None = all)

        Returns:
            List of option contract details
        """
        return await self.get_option_chain(symbol, exchange, max_expirations)

    def is_connection_healthy(self) -> bool:
        """
        Check if connection to IB is healthy.

        Returns:
            True if connected and responsive, False otherwise
        """
        return self.is_connected()

    def _create_stock_contract(
        self, symbol: str, exchange: Optional[str] = None
    ) -> Stock:
        """
        Create a stock contract with exchange specification.

        Args:
            symbol: Stock symbol
            exchange: Optional exchange (defaults to SMART)

        Returns:
            Stock contract
        """
        exchange = exchange or "SMART"
        return Stock(symbol, exchange, "USD")

    def _create_option_contract(
        self,
        symbol: str,
        expiration: str,
        strike: float,
        right: str,
        exchange: Optional[str] = None,
    ) -> Option:
        """
        Create an option contract with exchange specification.

        Args:
            symbol: Underlying symbol
            expiration: Expiration date (YYYYMMDD)
            strike: Strike price
            right: 'C' for call, 'P' for put
            exchange: Optional exchange (defaults to OPRA for US options)

        Returns:
            Option contract
        """
        exchange = exchange or "OPRA"
        return Option(symbol, expiration, strike, right, exchange)

    async def get_option_ticker(self, contract: Contract) -> Optional[Ticker]:
        """
        Get market data ticker for an option contract.

        Args:
            contract: Option contract

        Returns:
            Ticker with market data or None
        """
        if not self.is_connected():
            await self.connect()

        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(
                None, lambda: self.ib.reqMktData(contract, "", False, False)
            )

            # Wait for ticker to update
            await asyncio.sleep(0.5)

            return ticker
        except Exception as e:
            logger.error(f"Error getting ticker for {contract}: {e}")
            return None

    async def get_contract_details(
        self, contract: Contract
    ) -> Optional[ContractDetails]:
        """
        Get contract details for a contract.

        Args:
            contract: Contract to get details for

        Returns:
            ContractDetails or None
        """
        if not self.is_connected():
            await self.connect()

        try:
            loop = asyncio.get_event_loop()
            details = await loop.run_in_executor(
                None, lambda: self.ib.reqContractDetails(contract)
            )

            if details:
                return details[0]
            return None
        except Exception as e:
            logger.error(f"Error getting contract details for {contract}: {e}")
            return None


# Global connector instance
_connector: Optional[IBConnector] = None


async def get_connector() -> IBConnector:
    """Get or create the global IB connector instance."""
    global _connector
    if _connector is None:
        _connector = IBConnector()
        await _connector.connect()
    elif not _connector.is_connected():
        await _connector.connect()
    return _connector
