# Bifrost Options Trading Strategy Analyzer

A FastAPI-based web application that integrates with Interactive Brokers to fetch live options chain data, calculate strategy P&L profiles, and identify profitable opportunities using customizable filtering criteria.

## Features

- **Live Options Chain Data**: Fetch real-time options chain data from Interactive Brokers
- **Strategy Analysis**: Analyze option strategies including:
  - Covered Call
  - Iron Condor
- **Profit Analysis**: Calculate profit/loss profiles, breakeven points, and risk metrics
- **Custom Filtering**: Filter and rank strategies based on custom criteria (profit, risk/reward, probability, etc.)
- **REST API**: Full REST API for programmatic access
- **Real-time Data**: Uses live market data from Interactive Brokers

## Prerequisites

1. **Interactive Brokers Account**: You need an IB account (paper trading or live)
2. **IB TWS or IB Gateway**: Must be running and logged in
   - TWS (Trader Workstation) or IB Gateway
   - Paper trading: Port 7497 (TWS) or 4001 (Gateway)
   - Live trading: Port 7496 (TWS) or 4002 (Gateway)
3. **Python 3.8+**

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd bifrost-trader-option
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
# Interactive Brokers Connection Settings
IB_HOST=127.0.0.1
IB_PORT=7497          # 7497 for TWS paper, 7496 for TWS live
IB_CLIENT_ID=1

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=False

# Cache Settings
OPTIONS_CACHE_TTL=60  # seconds
```

## Running the Application

1. **Start IB TWS or IB Gateway**:
   - Log in to your account
   - Ensure API connections are enabled in settings

2. **Start the FastAPI server**:
```bash
python -m src.main
```

Or using uvicorn directly:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

3. **Access the API**:
   - API: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Health Check
```http
GET /api/health
```
Check if the application and IB connection are healthy.

### Get Options Chain
```http
GET /api/stocks/{symbol}/options?use_cache=true
```
Fetch options chain for a stock symbol.

**Example**:
```bash
curl http://localhost:8000/api/stocks/AAPL/options
```

**Response**:
```json
{
  "chain": {
    "symbol": "AAPL",
    "underlying_price": 150.25,
    "contracts": [...],
    "timestamp": "2024-01-15T10:30:00"
  },
  "expirations": ["20240119", "20240126", "20240216"],
  "strikes": [140, 145, 150, 155, 160]
}
```

### Analyze Strategy
```http
POST /api/strategies/analyze
```
Analyze a specific option strategy.

**Example - Covered Call**:
```bash
curl -X POST http://localhost:8000/api/strategies/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_type": "covered_call",
    "params": {
      "symbol": "AAPL",
      "stock_quantity": 100,
      "call_strike": 155,
      "call_expiration": "20240119",
      "stock_price": 150.25
    }
  }'
```

**Example - Iron Condor**:
```bash
curl -X POST http://localhost:8000/api/strategies/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_type": "iron_condor",
    "params": {
      "symbol": "AAPL",
      "put_sell_strike": 145,
      "put_buy_strike": 140,
      "call_sell_strike": 155,
      "call_buy_strike": 160,
      "expiration": "20240119",
      "quantity": 1
    }
  }'
```

### Find Profitable Opportunities
```http
GET /api/strategies/{strategy_type}?symbol={symbol}&expiration={expiration}&min_profit={min_profit}
```
Find and rank profitable strategy opportunities.

**Query Parameters**:
- `symbol`: Stock symbol (required)
- `expiration`: Expiration date YYYYMMDD (required for iron_condor)
- `min_profit`: Minimum profit filter
- `min_risk_reward`: Minimum risk/reward ratio
- `min_probability`: Minimum probability of profit
- `max_loss`: Maximum loss
- `min_premium_collected`: Minimum premium collected
- `limit`: Maximum number of results (default: 10)

**Example - Covered Call Opportunities**:
```bash
curl "http://localhost:8000/api/strategies/covered_call?symbol=AAPL&min_profit=100&min_risk_reward=0.5&limit=5"
```

**Example - Iron Condor Opportunities**:
```bash
curl "http://localhost:8000/api/strategies/iron_condor?symbol=AAPL&expiration=20240119&min_premium_collected=200&limit=10"
```

## Usage Examples

### Python Client Example

```python
import requests

# Get options chain
response = requests.get("http://localhost:8000/api/stocks/AAPL/options")
chain_data = response.json()

# Analyze covered call
analysis = requests.post(
    "http://localhost:8000/api/strategies/analyze",
    json={
        "strategy_type": "covered_call",
        "params": {
            "symbol": "AAPL",
            "stock_quantity": 100,
            "call_strike": 155,
            "call_expiration": "20240119",
            "stock_price": 150.25
        }
    }
)
results = analysis.json()

# Find profitable opportunities
opportunities = requests.get(
    "http://localhost:8000/api/strategies/covered_call",
    params={
        "symbol": "AAPL",
        "min_profit": 200,
        "min_risk_reward": 0.5,
        "limit": 5
    }
)
ranked_strategies = opportunities.json()
```

## Project Structure

```
bifrost-trader-option/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── ib_connector.py      # IB connection management
│   ├── options_chain.py     # Options data fetching
│   ├── analyzer.py          # Strategy analysis
│   ├── filter.py            # Profit filtering and ranking
│   ├── models.py            # Pydantic data models
│   ├── config.py            # Configuration
│   └── strategies/
│       ├── __init__.py
│       ├── base_strategy.py
│       ├── covered_call.py
│       └── iron_condor.py
├── docs/
│   ├── README.md            # Documentation index
│   └── DEPLOYMENT_ARCHITECTURE.md  # Multi-machine deployment plan
├── tests/
│   └── test_strategies.py
├── requirements.txt
├── .env.example
├── README.md
└── .gitignore
```

## Strategy Details

### Covered Call
- **Strategy**: Long stock + Short call option
- **Best for**: Bullish to neutral outlook, income generation
- **Max Profit**: Limited to (strike - stock_price) + premium
- **Max Loss**: Stock can go to zero

### Iron Condor
- **Strategy**: Sell put spread + Sell call spread
- **Best for**: Neutral outlook, range-bound stocks
- **Max Profit**: Net credit received
- **Max Loss**: Limited to spread width - net credit

## Filter Criteria

Strategies can be filtered and ranked by:
- **Max Profit**: Maximum potential profit
- **Risk/Reward Ratio**: Ratio of max profit to max loss
- **Probability of Profit**: Based on delta/Greeks
- **Premium Collected**: For credit strategies
- **Max Loss**: Maximum potential loss
- **Breakeven Range**: Width of profitable range

## Troubleshooting

### Connection Issues
- Ensure IB TWS/Gateway is running and logged in
- Check that API connections are enabled in TWS/Gateway settings
- Verify port number matches your configuration (7497 for paper, 7496 for live)
- Check firewall settings

### No Options Data
- Verify the symbol is valid and has options available
- Check market hours (options data may be limited outside trading hours)
- Ensure you have market data subscriptions in IB

### Performance Issues
- Adjust `OPTIONS_CACHE_TTL` in `.env` to cache data longer
- Limit the number of contracts analyzed
- Use `use_cache=true` when fetching options chains

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
The project follows PEP 8 style guidelines.

## License

Apache License 2.0

## Disclaimer

This software is for educational and research purposes only. Trading options involves substantial risk of loss. Past performance is not indicative of future results. Always consult with a qualified financial advisor before making investment decisions.

## Documentation

- **Main README**: This file
- **Deployment Architecture**: See [docs/DEPLOYMENT_ARCHITECTURE.md](docs/DEPLOYMENT_ARCHITECTURE.md) for multi-machine deployment setup
- **API Documentation**: Available at `/docs` endpoint when FastAPI is running

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check deployment architecture documentation in `docs/` directory
4. Check IB API documentation for connection issues


