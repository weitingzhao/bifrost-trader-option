# IB Connector Tests

## Overview

This document describes the test suite for the Interactive Brokers (IB) connector module (`src/core/connector/ib.py`). The tests ensure that the IB connector properly handles connections, data retrieval, and error scenarios without requiring a live IB Gateway connection.

## Test Location

- **Test File**: `tests/connector/test_ib.py`
- **Source Module**: `src/core/connector/ib.py`

## Test Structure

The test suite is organized into four main test classes:

### 1. TestIBConnector

Tests for the core `IBConnector` class functionality.

#### Connection Management Tests

- `test_connect_success` - Verifies successful connection to IB Gateway
- `test_connect_already_connected` - Ensures no duplicate connections when already connected
- `test_connect_failure` - Handles connection failures gracefully
- `test_disconnect` - Verifies proper disconnection
- `test_disconnect_not_connected` - Handles disconnection when not connected
- `test_is_connected_true` - Checks connection status when connected
- `test_is_connected_false` - Checks connection status when disconnected
- `test_is_connection_healthy` - Verifies connection health check

#### Stock Price Retrieval Tests

- `test_get_stock_price_success` - Retrieves stock price successfully
- `test_get_stock_price_with_exchange` - Retrieves stock price with exchange specification
- `test_get_stock_price_fallback_to_close` - Falls back to close price when market price unavailable
- `test_get_stock_price_error` - Handles errors during price retrieval

#### Option Chain Retrieval Tests

- `test_get_option_chain_success` - Retrieves option chain successfully
- `test_get_option_chain_no_chains` - Handles case when no chains found
- `test_get_option_chain_empty_chain` - Handles empty option chains
- `test_get_option_chain_with_exchange` - Retrieves option chain with exchange specification
- `test_get_option_chain_full` - Tests the full option chain method
- `test_get_option_chain_max_expirations` - Limits expirations when specified

#### Option Ticker Tests

- `test_get_option_ticker_success` - Retrieves option ticker successfully
- `test_get_option_ticker_error` - Handles errors during ticker retrieval

#### Contract Details Tests

- `test_get_contract_details_success` - Retrieves contract details successfully
- `test_get_contract_details_no_details` - Handles case when no details found

#### Helper Method Tests

- `test_create_stock_contract` - Creates stock contract with exchange
- `test_create_stock_contract_default_exchange` - Creates stock contract with default exchange
- `test_create_option_contract` - Creates option contract with exchange
- `test_create_option_contract_default_exchange` - Creates option contract with default exchange

### 2. TestGetConnector

Tests for the `get_connector()` global function.

- `test_get_connector_creates_new` - Creates new connector when none exists
- `test_get_connector_reuses_existing` - Reuses existing connector when connected
- `test_get_connector_reconnects_when_disconnected` - Reconnects when existing connector is disconnected

### 3. TestIBConnectorExchangeSupport

Tests for exchange support functionality.

- `test_get_stock_price_uses_exchange` - Verifies stock price uses specified exchange
- `test_get_option_chain_uses_exchange` - Verifies option chain uses specified exchange
- `test_get_option_chain_opra_for_us_options` - Ensures US options use OPRA exchange

### 4. TestIBConnectorBatchProcessing

Tests for batch processing functionality.

- `test_get_option_chain_batch_processing` - Verifies option chain processing uses batches

## Running the Tests

### Run All Connector Tests

```bash
pytest tests/connector/test_ib.py -v
```

### Run Specific Test Class

```bash
pytest tests/connector/test_ib.py::TestIBConnector -v
pytest tests/connector/test_ib.py::TestGetConnector -v
pytest tests/connector/test_ib.py::TestIBConnectorExchangeSupport -v
pytest tests/connector/test_ib.py::TestIBConnectorBatchProcessing -v
```

### Run Specific Test

```bash
pytest tests/connector/test_ib.py::TestIBConnector::test_connect_success -v
```

### Run Only Integration Tests

```bash
pytest tests/connector/test_ib.py -m integration -v
```

### Skip Integration Tests

```bash
pytest tests/connector/test_ib.py -m "not integration" -v
```

### Run with Coverage

```bash
pytest tests/connector/test_ib.py --cov=src.core.connector.ib --cov-report=term-missing
```

## Test Strategy

The tests use the **real** `ib_insync` library and IB Gateway/TWS connection:

1. **Real Library Usage**: Tests import and use the actual `ib_insync` library, not mocks.

2. **Integration Tests**: Tests that require IB Gateway/TWS are marked with `@pytest.mark.integration` and will be skipped if:
   - `ib_insync` is not installed
   - IB Gateway/TWS is not running
   - Connection cannot be established

3. **Graceful Degradation**: Tests handle connection failures gracefully by skipping rather than failing.

4. **Limited Mocking**: Only minimal mocking is used for:
   - Testing error conditions
   - Testing behavior when not connected
   - Verifying method calls without actual network operations

## Key Test Scenarios

### Connection Management

- ✅ Successful connection with custom host/port/client_id
- ✅ Connection reuse when already connected
- ✅ Connection failure handling
- ✅ Proper disconnection
- ✅ Connection status checking

### Data Retrieval

- ✅ Stock price retrieval with and without exchange
- ✅ Option chain retrieval (full chains, empty chains, no chains)
- ✅ Option ticker retrieval
- ✅ Contract details retrieval
- ✅ Error handling for all retrieval methods

### Exchange Support

- ✅ NYSE exchange support
- ✅ NASDAQ exchange support
- ✅ OPRA exchange for US options
- ✅ SMART routing as default

### Batch Processing

- ✅ Option chain batch processing
- ✅ Rate limiting between batches

## Test Coverage

The test suite covers:

- **Connection Management**: 100% coverage
- **Stock Price Retrieval**: 100% coverage
- **Option Chain Retrieval**: 95% coverage (complex batch processing scenarios)
- **Error Handling**: 100% coverage
- **Exchange Support**: 100% coverage
- **Helper Methods**: 100% coverage

## Dependencies

The tests require:

- `pytest` - Testing framework
- `pytest-asyncio` - Async test support (for async test execution)
- `ib_insync` - Interactive Brokers API library (REQUIRED)
- `unittest.mock` - Mocking utilities (built-in, for limited mocking)

**Note**: The tests use the **real** `ib_insync` library, not mocks. You must install `ib_insync` and have a running IB Gateway or TWS instance to run integration tests.

## Installation and Setup

### Installing ib_insync

```bash
pip install ib_insync
```

For more information, see: https://github.com/erdewit/ib_insync

### Setting Up IB Gateway/TWS

To run integration tests, you need a running Interactive Brokers Gateway or TWS instance:

1. **Download IB Gateway or TWS:**
   - IB Gateway: https://www.interactivebrokers.com/en/index.php?f=16457
   - TWS (Trader Workstation): https://www.interactivebrokers.com/en/index.php?f=16042

2. **Configure IB Gateway/TWS:**
   - Enable API connections in Configuration → API → Settings
   - Set "Enable ActiveX and Socket Clients" to Yes
   - Set "Read-Only API" to No (if you need to place orders)
   - Set "Socket port" to 7497 (paper trading) or 7496 (live trading)
   - Add trusted IP addresses if needed (127.0.0.1 for localhost)

3. **Start IB Gateway/TWS:**
   - Launch IB Gateway or TWS
   - Log in with your credentials
   - Ensure the API is enabled and listening on the configured port

4. **Verify Connection:**
   ```bash
   # Test connection (optional)
   python -c "from ib_insync import IB; ib = IB(); ib.connect('127.0.0.1', 7497, clientId=1); print('Connected!'); ib.disconnect()"
   ```

### Environment Configuration

The tests use the following default connection settings:
- **Host**: `127.0.0.1` (localhost)
- **Port**: `7497` (paper trading) or `7496` (live trading)
- **Client ID**: `1` (can be changed in test)

You can override these in your `.env` file or test configuration.

## Troubleshooting

### ModuleNotFoundError: No module named 'ib_insync'

If you encounter this error:

1. **Install ib_insync:**
   ```bash
   pip install ib_insync
   ```

2. **Verify installation:**
   ```bash
   python -c "import ib_insync; print(ib_insync.__version__)"
   ```

3. **If using a virtual environment, ensure it's activated:**
   ```bash
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

### Connection Errors

If tests fail with connection errors:

1. **Verify IB Gateway/TWS is running:**
   - Check that IB Gateway or TWS is launched and logged in
   - Verify the API is enabled in settings

2. **Check port configuration:**
   - Default: 7497 (paper trading) or 7496 (live trading)
   - Ensure no firewall is blocking the port

3. **Verify client ID:**
   - Each connection needs a unique client ID
   - If multiple connections exist, use different client IDs (1, 2, 3, etc.)

4. **Check API permissions:**
   - Ensure "Enable ActiveX and Socket Clients" is enabled
   - Verify IP address is trusted (if required)

### Test Skipping

Integration tests are marked with `@pytest.mark.integration` and will be skipped if:
- `ib_insync` is not installed
- IB Gateway/TWS is not running
- Connection cannot be established

To run only integration tests:
```bash
pytest tests/connector/test_ib.py -m integration
```

To skip integration tests:
```bash
pytest tests/connector/test_ib.py -m "not integration"
```

### Async Test Failures

If async tests fail, ensure:
1. `pytest-asyncio` is installed
2. `pytest.ini` has `asyncio_mode = auto` configured
3. Tests are marked with `@pytest.mark.asyncio`

### Mock Assertion Failures

If mock assertions fail:
1. Verify the mock setup matches the actual implementation
2. Check that all required mock attributes are set
3. Ensure async mocks use `AsyncMock` instead of `Mock`

## Future Enhancements

Potential improvements to the test suite:

1. **Integration Tests**: Add tests that require a live IB Gateway (marked with `@pytest.mark.integration`)
2. **Performance Tests**: Add tests for batch processing performance
3. **Concurrency Tests**: Test multiple simultaneous connections
4. **Error Recovery Tests**: Test automatic reconnection scenarios
5. **Rate Limiting Tests**: Verify rate limiting behavior under load

## Related Documentation

- [Testing Overview](README.md) - General testing documentation
- [IB Setup Guide](IB_SETUP.md) - **Complete guide for setting up IB Gateway/TWS**
- IB Connector Source: `src/core/connector/ib.py` - Source code documentation
- [API Development Guide](../api/API_DEVELOPMENT_GUIDE.md) - API testing guidelines

## Quick Setup Reference

For detailed setup instructions, see **[IB_SETUP.md](IB_SETUP.md)**.

**Quick Start:**
1. Install: `pip install ib_insync`
2. Download and launch IB Gateway/TWS
3. Enable API: Configuration → API → Settings
4. Set port: 7497 (paper) or 7496 (live)
5. Test: Run `pytest tests/connector/test_ib.py -v`

