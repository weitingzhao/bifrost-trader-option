# Bifrost Frontend

Production trading interface built with React/Vue.

## Status

⚠️ **Placeholder**: This is a placeholder structure. Full frontend implementation will be completed in Phase 4.

## Planned Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Page components
│   ├── services/       # API client (calls FastAPI)
│   └── utils/          # Utility functions
├── public/             # Static assets
└── package.json        # Dependencies
```

## API Client

The API client (`src/services/api.js`) provides functions to interact with the FastAPI backend:

- `fetchOptionsChain(symbol, useCache)` - Get option chain data
- `analyzeStrategy(strategyParams)` - Analyze a trading strategy
- `getStrategyOpportunities(strategyType, filters)` - Get strategy opportunities
- `getHistoricalData(symbol, hours)` - Get historical option data
- `healthCheck()` - Check API health

## Phase 4 Implementation

In Phase 4, this will be expanded to include:

- Full React/Vue application structure
- Trading interface components
- Real-time option chain visualization
- Strategy builder UI
- TradingView Lightweight Charts integration
- Responsive design for mobile and desktop

## Deployment

The frontend will be deployed to Web-Server (10.0.0.75) and served via Nginx reverse proxy.

