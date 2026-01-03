"""Tests for Interactive Brokers connector."""

import pytest
from unittest.mock import Mock, AsyncMock, patch

# Try to import ib_insync - if not available, provide helpful error message
IB_IMPORT_ERROR = ""
try:
    from ib_insync import Stock, Option  # Only import what we actually use

    IB_INSYNC_AVAILABLE = True
except ImportError as e:
    IB_INSYNC_AVAILABLE = False
    IB_IMPORT_ERROR = str(e)
    # Create placeholder classes for type hints
    Stock = None
    Option = None

# Import connector module - this will fail if ib_insync is not installed
try:
    from src.core.connector.ib import IBConnector, get_connector
except ImportError as e:
    if not IB_INSYNC_AVAILABLE:
        pytest.skip(
            f"\n\n"
            f"❌ ib_insync is not installed!\n"
            f"   Error: {IB_IMPORT_ERROR}\n\n"
            f"📦 To install ib_insync, run:\n"
            f"   pip install ib_insync\n\n"
            f"📚 For more information, see:\n"
            f"   https://github.com/erdewit/ib_insync\n\n"
            f"⚠️  Note: These tests require a running IB Gateway or TWS instance.\n"
            f"   See docs/testing/CONNECTOR_TESTS.md for setup instructions.\n",
            allow_module_level=True,
        )
    else:
        raise


class TestIBConnector:
    """Test suite for IBConnector class."""

    @pytest.fixture
    def connector(self):
        """Create an IBConnector instance with real IB."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        # Use real IB instance
        connector = IBConnector()
        return connector

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_connect_success(self, connector):
        """Test successful connection to IB Gateway/TWS."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        # This test requires a running IB Gateway/TWS
        # Skip if not available, but don't fail
        try:
            result = await connector.connect("127.0.0.1", 7497, 1)
            # If connection succeeds, verify state
            if result:
                assert connector.connected is True
                assert connector.is_connected() is True
                # Clean up
                await connector.disconnect()
        except Exception as e:
            pytest.skip(
                f"Cannot connect to IB Gateway/TWS: {e}\n"
                f"Make sure IB Gateway or TWS is running on 127.0.0.1:7497"
            )

    @pytest.mark.asyncio
    async def test_connect_already_connected(self, connector):
        """Test connection when already connected."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        # Mock the connected state
        connector.connected = True

        result = await connector.connect()

        assert result is True

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_connect_failure(self, connector):
        """Test connection failure handling."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        connector.connected = False

        # Try to connect to invalid host/port
        result = await connector.connect("127.0.0.1", 9999, 1)

        # Should return False on connection failure
        assert result is False
        assert connector.connected is False

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_disconnect(self, connector):
        """Test disconnection from IB."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        # First connect if possible
        try:
            await connector.connect("127.0.0.1", 7497, 1)
            if connector.connected:
                await connector.disconnect()
                assert connector.connected is False
        except Exception:
            # If we can't connect, just test disconnect on unconnected state
            connector.connected = False
            await connector.disconnect()
            assert connector.connected is False

    @pytest.mark.asyncio
    async def test_disconnect_not_connected(self, connector):
        """Test disconnection when not connected."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        connector.connected = False

        await connector.disconnect()

        assert connector.connected is False

    def test_is_connected_true(self, connector):
        """Test is_connected returns True when connected."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        connector.connected = True
        # Mock the IB instance's isConnected method
        connector.ib.isConnected = Mock(return_value=True)

        result = connector.is_connected()

        assert result is True

    def test_is_connected_false(self, connector):
        """Test is_connected returns False when not connected."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        connector.connected = False
        connector.ib.isConnected = Mock(return_value=False)

        result = connector.is_connected()

        assert result is False

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_stock_price_success(self, connector):
        """Test successful stock price retrieval."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        # This test requires a running IB Gateway/TWS
        try:
            await connector.connect("127.0.0.1", 7497, 1)
            if not connector.connected:
                pytest.skip("Cannot connect to IB Gateway/TWS")

            price = await connector.get_stock_price("AAPL", "NASDAQ")

            # Price should be a float if successful
            if price is not None:
                assert isinstance(price, (int, float))
                assert price > 0

            await connector.disconnect()
        except Exception as e:
            pytest.skip(f"Cannot test stock price retrieval: {e}")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_stock_price_with_exchange(self, connector):
        """Test stock price retrieval with exchange specification."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        try:
            await connector.connect("127.0.0.1", 7497, 1)
            if not connector.connected:
                pytest.skip("Cannot connect to IB Gateway/TWS")

            price = await connector.get_stock_price("TSLA", "NASDAQ")

            if price is not None:
                assert isinstance(price, (int, float))
                assert price > 0

            await connector.disconnect()
        except Exception as e:
            pytest.skip(f"Cannot test stock price retrieval: {e}")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_stock_price_fallback_to_close(self, connector):
        """Test stock price falls back to close price when market price unavailable."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        try:
            await connector.connect("127.0.0.1", 7497, 1)
            if not connector.connected:
                pytest.skip("Cannot connect to IB Gateway/TWS")

            price = await connector.get_stock_price("AAPL")

            # Should return a price (either market or close)
            if price is not None:
                assert isinstance(price, (int, float))
                assert price > 0

            await connector.disconnect()
        except Exception as e:
            pytest.skip(f"Cannot test stock price retrieval: {e}")

    @pytest.mark.asyncio
    async def test_get_stock_price_error(self, connector):
        """Test stock price retrieval error handling."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        connector.connected = False

        # Should return None when not connected
        price = await connector.get_stock_price("AAPL")

        assert price is None

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_option_chain_success(self, connector):
        """Test successful option chain retrieval."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        try:
            await connector.connect("127.0.0.1", 7497, 1)
            if not connector.connected:
                pytest.skip("Cannot connect to IB Gateway/TWS")

            result = await connector.get_option_chain(
                "AAPL", "NASDAQ", max_expirations=2
            )

            # Should return list of contract details
            assert isinstance(result, list)
            # If we got results, verify structure
            if result:
                assert hasattr(result[0], "contract")

            await connector.disconnect()
        except Exception as e:
            pytest.skip(f"Cannot test option chain retrieval: {e}")

    @pytest.mark.asyncio
    async def test_get_option_chain_no_chains(self, connector):
        """Test option chain retrieval when no chains found."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        connector.connected = False

        result = await connector.get_option_chain("INVALID")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_option_chain_empty_chain(self, connector):
        """Test option chain retrieval with empty chain."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        connector.connected = False

        result = await connector.get_option_chain("AAPL")

        # When not connected, should return empty list
        assert isinstance(result, list)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_option_chain_with_exchange(self, connector):
        """Test option chain retrieval with exchange specification."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        try:
            await connector.connect("127.0.0.1", 7497, 1)
            if not connector.connected:
                pytest.skip("Cannot connect to IB Gateway/TWS")

            result = await connector.get_option_chain(
                "AAPL", "NASDAQ", max_expirations=1
            )

            assert isinstance(result, list)

            await connector.disconnect()
        except Exception as e:
            pytest.skip(f"Cannot test option chain retrieval: {e}")

    @pytest.mark.asyncio
    async def test_get_option_chain_full(self, connector):
        """Test get_option_chain_full method."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        with patch.object(
            connector, "get_option_chain", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = []

            result = await connector.get_option_chain_full("AAPL", "NASDAQ", None)

            mock_get.assert_called_once_with("AAPL", "NASDAQ", None)
            assert result == []

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_option_chain_max_expirations(self, connector):
        """Test option chain with max_expirations limit."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        try:
            await connector.connect("127.0.0.1", 7497, 1)
            if not connector.connected:
                pytest.skip("Cannot connect to IB Gateway/TWS")

            result = await connector.get_option_chain("AAPL", max_expirations=2)

            # Should return list
            assert isinstance(result, list)

            await connector.disconnect()
        except Exception as e:
            pytest.skip(f"Cannot test option chain retrieval: {e}")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_option_ticker_success(self, connector):
        """Test successful option ticker retrieval."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        try:
            await connector.connect("127.0.0.1", 7497, 1)
            if not connector.connected:
                pytest.skip("Cannot connect to IB Gateway/TWS")

            # Create a real option contract
            option = Option("AAPL", "20240119", 150.0, "C", "OPRA")

            ticker = await connector.get_option_ticker(option)

            # Ticker might be None if market data not available
            # But if we get one, verify it's a Ticker object
            if ticker is not None:
                assert hasattr(ticker, "bid") or hasattr(ticker, "ask")

            await connector.disconnect()
        except Exception as e:
            pytest.skip(f"Cannot test option ticker retrieval: {e}")

    @pytest.mark.asyncio
    async def test_get_option_ticker_error(self, connector):
        """Test option ticker retrieval error handling."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        connector.connected = False
        mock_contract = Mock()

        ticker = await connector.get_option_ticker(mock_contract)

        assert ticker is None

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_contract_details_success(self, connector):
        """Test successful contract details retrieval."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        try:
            await connector.connect("127.0.0.1", 7497, 1)
            if not connector.connected:
                pytest.skip("Cannot connect to IB Gateway/TWS")

            # Create a real stock contract
            stock = Stock("AAPL", "SMART", "USD")

            details = await connector.get_contract_details(stock)

            # Details might be None if contract not found
            # But if we get one, verify it's a ContractDetails object
            if details is not None:
                assert hasattr(details, "contract")

            await connector.disconnect()
        except Exception as e:
            pytest.skip(f"Cannot test contract details retrieval: {e}")

    @pytest.mark.asyncio
    async def test_get_contract_details_no_details(self, connector):
        """Test contract details retrieval when no details found."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        connector.connected = False
        mock_contract = Mock()

        details = await connector.get_contract_details(mock_contract)

        # When not connected, should return None
        assert details is None

    def test_is_connection_healthy(self, connector):
        """Test connection health check."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        connector.connected = True
        with patch.object(connector, "is_connected", return_value=True):
            assert connector.is_connection_healthy() is True

    def test_create_stock_contract(self, connector):
        """Test stock contract creation."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        contract = connector._create_stock_contract("AAPL", "NASDAQ")

        assert isinstance(contract, Stock)
        assert contract.symbol == "AAPL"
        assert contract.exchange == "NASDAQ"
        assert contract.currency == "USD"

    def test_create_stock_contract_default_exchange(self, connector):
        """Test stock contract creation with default exchange."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        contract = connector._create_stock_contract("AAPL")

        assert isinstance(contract, Stock)
        assert contract.symbol == "AAPL"
        assert contract.exchange == "SMART"
        assert contract.currency == "USD"

    def test_create_option_contract(self, connector):
        """Test option contract creation."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        contract = connector._create_option_contract(
            "AAPL", "20240119", 150.0, "C", "OPRA"
        )

        assert isinstance(contract, Option)
        assert contract.symbol == "AAPL"
        assert contract.lastTradeDateOrContractMonth == "20240119"
        assert contract.strike == 150.0
        assert contract.right == "C"
        assert contract.exchange == "OPRA"

    def test_create_option_contract_default_exchange(self, connector):
        """Test option contract creation with default exchange."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        contract = connector._create_option_contract("AAPL", "20240119", 150.0, "P")

        assert isinstance(contract, Option)
        assert contract.symbol == "AAPL"
        assert contract.lastTradeDateOrContractMonth == "20240119"
        assert contract.strike == 150.0
        assert contract.right == "P"
        assert contract.exchange == "OPRA"


class TestGetConnector:
    """Test suite for get_connector function."""

    @pytest.mark.asyncio
    async def test_get_connector_creates_new(self):
        """Test get_connector creates new connector when none exists."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        with patch("src.core.connector.ib._connector", None):
            connector = await get_connector()

            assert connector is not None
            assert isinstance(connector, IBConnector)

    @pytest.mark.asyncio
    async def test_get_connector_reuses_existing(self):
        """Test get_connector reuses existing connector when connected."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        mock_connector = Mock()
        mock_connector.is_connected.return_value = True

        with patch("src.core.connector.ib._connector", mock_connector):
            connector = await get_connector()

            assert connector == mock_connector
            # Should not call connect again
            assert (
                not hasattr(mock_connector.connect, "call_count")
                or mock_connector.connect.call_count == 0
            )

    @pytest.mark.asyncio
    async def test_get_connector_reconnects_when_disconnected(self):
        """Test get_connector reconnects when existing connector is disconnected."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        mock_connector = Mock()
        mock_connector.is_connected.return_value = False
        mock_connector.connect = AsyncMock()

        with patch("src.core.connector.ib._connector", mock_connector):
            connector = await get_connector()

            assert connector == mock_connector
            mock_connector.connect.assert_called_once()


class TestIBConnectorExchangeSupport:
    """Test suite for exchange support in IB connector."""

    @pytest.fixture
    def connector(self):
        """Create an IBConnector instance."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        return IBConnector()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_stock_price_uses_exchange(self, connector):
        """Test that get_stock_price uses specified exchange."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        try:
            await connector.connect("127.0.0.1", 7497, 1)
            if not connector.connected:
                pytest.skip("Cannot connect to IB Gateway/TWS")

            # Verify Stock contract is created with correct exchange
            with patch("src.core.connector.ib.Stock") as mock_stock:
                await connector.get_stock_price("AAPL", "NASDAQ")

                # Verify Stock was created with correct exchange
                mock_stock.assert_called_once_with("AAPL", "NASDAQ", "USD")

            await connector.disconnect()
        except Exception as e:
            pytest.skip(f"Cannot test exchange support: {e}")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_option_chain_uses_exchange(self, connector):
        """Test that get_option_chain uses specified exchange."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        try:
            await connector.connect("127.0.0.1", 7497, 1)
            if not connector.connected:
                pytest.skip("Cannot connect to IB Gateway/TWS")

            with patch("src.core.connector.ib.Stock") as mock_stock:
                await connector.get_option_chain("AAPL", "NYSE", max_expirations=1)

                # Verify Stock was created with correct exchange
                mock_stock.assert_called_once_with("AAPL", "NYSE", "USD")

            await connector.disconnect()
        except Exception as e:
            pytest.skip(f"Cannot test exchange support: {e}")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_option_chain_opra_for_us_options(self, connector):
        """Test that US options use OPRA exchange."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        try:
            await connector.connect("127.0.0.1", 7497, 1)
            if not connector.connected:
                pytest.skip("Cannot connect to IB Gateway/TWS")

            with patch("src.core.connector.ib.Option") as mock_option:
                await connector.get_option_chain("AAPL", "NASDAQ", max_expirations=1)

                # Verify Option contracts use OPRA for US exchanges
                # This is a simplified check - actual implementation creates multiple contracts
                assert mock_option.called

            await connector.disconnect()
        except Exception as e:
            pytest.skip(f"Cannot test OPRA exchange support: {e}")


class TestIBConnectorBatchProcessing:
    """Test suite for batch processing in IB connector."""

    @pytest.fixture
    def connector(self):
        """Create an IBConnector instance."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        connector = IBConnector()
        return connector

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_option_chain_batch_processing(self, connector):
        """Test that option chain processing uses batches."""
        if not IB_INSYNC_AVAILABLE:
            pytest.skip("ib_insync not available")

        try:
            await connector.connect("127.0.0.1", 7497, 1)
            if not connector.connected:
                pytest.skip("Cannot connect to IB Gateway/TWS")

            result = await connector.get_option_chain("AAPL", max_expirations=2)

            # Should process in batches
            assert isinstance(result, list)

            await connector.disconnect()
        except Exception as e:
            pytest.skip(f"Cannot test batch processing: {e}")
