# Bifrost Analytics Dashboard

Streamlit analytics dashboard for strategy performance analysis and option chain visualization.

## Features

- **Strategy Performance**: Track and analyze historical strategy performance
- **Option Chain Viewer**: Visualize option chains with interactive Plotly charts
- **Profit Analysis**: Analyze profit/loss profiles for strategies

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## Pages

1. **Home** (`app.py`) - Main dashboard page
2. **Strategy Performance** (`pages/strategy_performance.py`) - Performance metrics and charts
3. **Option Chain Viewer** (`pages/option_chain_viewer.py`) - Interactive option chain visualization
4. **Profit Analysis** (`pages/profit_analysis.py`) - P&L profiles and Greeks analysis

## Database Connection

⚠️ **Note**: Database connection will be implemented in Phase 2. Currently, the dashboard shows placeholder UI components.

Once connected, the dashboard will:
- Query strategy history from PostgreSQL
- Display real-time option chain data
- Show historical performance metrics
- Generate interactive charts with actual data

