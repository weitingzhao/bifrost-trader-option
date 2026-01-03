# Interactive Brokers Setup Guide

This guide explains how to set up Interactive Brokers Gateway or TWS for testing and development with the Bifrost project.

## Overview

The Bifrost project uses `ib_insync` to connect to Interactive Brokers for real-time market data and option chain retrieval. To run tests and use the application, you need:

1. **ib_insync library** - Python library for IB API
2. **IB Gateway or TWS** - Interactive Brokers client software
3. **API Configuration** - Enable API access in IB Gateway/TWS

## Installation

### Step 1: Install ib_insync

```bash
pip install ib_insync
```

Verify installation:
```bash
python -c "import ib_insync; print(ib_insync.__version__)"
```

### Step 2: Download IB Gateway or TWS

**Option A: IB Gateway (Recommended for Automated Systems)**
- Download: https://www.interactivebrokers.com/en/index.php?f=16457
- Lightweight, designed for API connections
- No GUI, runs in background

**Option B: TWS (Trader Workstation)**
- Download: https://www.interactivebrokers.com/en/index.php?f=16042
- Full-featured trading platform
- Includes API access

### Step 3: Install and Launch IB Gateway/TWS

1. Download and install IB Gateway or TWS
2. Launch the application
3. Log in with your Interactive Brokers credentials
4. **Important**: Use Paper Trading account for testing (recommended)

## API Configuration

### Enable API Access

1. **In IB Gateway/TWS:**
   - Go to **Configuration** → **API** → **Settings**
   - Check **"Enable ActiveX and Socket Clients"**
   - Set **"Socket port"** to:
     - `7497` for Paper Trading
     - `7496` for Live Trading
   - Set **"Read-Only API"** to:
     - `Yes` if you only need market data (recommended for testing)
     - `No` if you need to place orders

2. **Trusted IP Addresses (Optional):**
   - Add `127.0.0.1` to trusted IPs for localhost connections
   - Add your server IP if connecting remotely

3. **Master API Client ID:**
   - Set to a unique number (default: 0)
   - Each connection needs a unique client ID

### Configuration Summary

```
✅ Enable ActiveX and Socket Clients: Yes
✅ Socket port: 7497 (Paper) or 7496 (Live)
✅ Read-Only API: Yes (for testing)
✅ Trusted IPs: 127.0.0.1 (localhost)
```

## Verification

### Test Connection

Create a simple test script to verify the connection:

```python
import asyncio
from ib_insync import IB

async def test_connection():
    ib = IB()
    try:
        await ib.connect('127.0.0.1', 7497, clientId=1)
        print("✅ Successfully connected to IB Gateway/TWS")
        print(f"   Server version: {ib.serverVersion()}")
        await ib.disconnect()
        print("✅ Disconnected successfully")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure IB Gateway/TWS is running")
        print("2. Check API is enabled in Configuration → API → Settings")
        print("3. Verify port is correct (7497 for paper, 7496 for live)")

asyncio.run(test_connection())
```

Save as `test_ib_connection.py` and run:
```bash
python test_ib_connection.py
```

## Environment Configuration

### .env File

Add IB connection settings to your `.env` file:

```bash
# IB Connection Settings
IB_HOST=127.0.0.1
IB_PORT=7497          # 7497 for paper trading, 7496 for live trading
IB_CLIENT_ID=1        # Unique client ID for this connection

# IB Data Collection Settings
IB_COLLECTION_BATCH_SIZE=50
IB_COLLECTION_BATCH_DELAY=0.1
IB_COLLECTION_MAX_RETRIES=3
IB_COLLECTION_RETRY_DELAY=1.0

# IB Exchange Settings
IB_DEFAULT_STOCK_EXCHANGE=SMART
IB_DEFAULT_OPTION_EXCHANGE=OPRA
```

### Multiple Connections

If you need multiple simultaneous connections, use different client IDs:

```bash
# FastAPI real-time requests
IB_CLIENT_ID=1

# Data collector service
IB_CLIENT_ID=2

# Background analysis jobs
IB_CLIENT_ID=3
```

## Running Tests

### Prerequisites

1. **Install ib_insync:**
   ```bash
   pip install ib_insync
   ```

2. **Start IB Gateway/TWS:**
   - Launch IB Gateway or TWS
   - Log in
   - Ensure API is enabled

3. **Run Tests:**
   ```bash
   # Run all connector tests
   pytest tests/connector/test_ib.py -v
   
   # Run only integration tests (require IB Gateway/TWS)
   pytest tests/connector/test_ib.py -m integration -v
   
   # Skip integration tests (unit tests only)
   pytest tests/connector/test_ib.py -m "not integration" -v
   ```

### Test Behavior

- **Unit Tests**: Run without IB Gateway/TWS (test contract creation, etc.)
- **Integration Tests**: Require running IB Gateway/TWS
  - Will be skipped if connection cannot be established
  - Will be skipped if `ib_insync` is not installed

## Troubleshooting

### Connection Refused

**Error**: `ConnectionRefusedError: [Errno 61] Connection refused`

**Solutions**:
1. Verify IB Gateway/TWS is running
2. Check API is enabled in Configuration → API → Settings
3. Verify port matches configuration (7497 or 7496)
4. Check firewall settings

### Client ID Already in Use

**Error**: `Client already connected`

**Solutions**:
1. Use a different client ID
2. Disconnect existing connections
3. Restart IB Gateway/TWS

### API Not Enabled

**Error**: `Connection timeout` or `Connection refused`

**Solutions**:
1. Go to Configuration → API → Settings
2. Enable "Enable ActiveX and Socket Clients"
3. Restart IB Gateway/TWS
4. Verify port is correct

### Market Data Not Available

**Error**: `No market data available` or empty results

**Solutions**:
1. Ensure you have market data subscriptions enabled
2. Check account permissions for market data
3. Verify symbol is valid and trading
4. For paper trading, some data may be delayed

### Paper Trading vs Live Trading

**Paper Trading (Recommended for Testing)**:
- Port: `7497`
- Safe for testing
- May have delayed data
- No real money at risk

**Live Trading**:
- Port: `7496`
- Real market data
- Real money at risk
- Requires careful configuration

## Security Best Practices

1. **Use Paper Trading for Development**: Always test with paper trading first
2. **Read-Only API**: Enable "Read-Only API" unless you need to place orders
3. **Firewall**: Restrict API access to trusted IPs
4. **Credentials**: Never commit IB credentials to version control
5. **Client IDs**: Use unique client IDs for each connection

## Additional Resources

- **ib_insync Documentation**: https://ib-insync.readthedocs.io/
- **IB API Documentation**: https://interactivebrokers.github.io/tws-api/
- **IB Gateway Download**: https://www.interactivebrokers.com/en/index.php?f=16457
- **TWS Download**: https://www.interactivebrokers.com/en/index.php?f=16042

## Quick Start Checklist

- [ ] Install `ib_insync`: `pip install ib_insync`
- [ ] Download and install IB Gateway or TWS
- [ ] Launch IB Gateway/TWS and log in
- [ ] Enable API in Configuration → API → Settings
- [ ] Set port to 7497 (paper) or 7496 (live)
- [ ] Add `127.0.0.1` to trusted IPs (optional)
- [ ] Test connection with verification script
- [ ] Update `.env` file with connection settings
- [ ] Run tests: `pytest tests/connector/test_ib.py -v`

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify IB Gateway/TWS is running and API is enabled
3. Review test output for specific error messages
4. Check `ib_insync` documentation for API-specific issues
5. Review IB API documentation for connection requirements

