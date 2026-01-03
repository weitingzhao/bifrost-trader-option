"""Streamlit analytics dashboard for strategy performance."""
import streamlit as st

st.set_page_config(
    page_title="Bifrost Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Bifrost Options Trading Analytics")
st.markdown("Strategy performance analysis and option chain visualization")

st.sidebar.title("Navigation")
st.sidebar.markdown("### Analytics Pages")
st.sidebar.page_link("app.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/strategy_performance.py", label="Strategy Performance", icon="📈")
st.sidebar.page_link("pages/option_chain_viewer.py", label="Option Chain Viewer", icon="🔍")
st.sidebar.page_link("pages/profit_analysis.py", label="Profit Analysis", icon="💰")
st.sidebar.page_link("pages/backtesting.py", label="Backtesting", icon="📊")

st.markdown("""
## Welcome to Bifrost Analytics

This dashboard provides comprehensive analytics for your options trading strategies.

### Available Features:

1. **Strategy Performance** - Track and analyze historical strategy performance
2. **Option Chain Viewer** - Visualize option chains with interactive charts
3. **Profit Analysis** - Analyze profit/loss profiles for strategies
4. **Backtesting** - Backtest strategies using historical data with VectorBT

### Getting Started

Select a page from the sidebar to begin analyzing your trading data.
""")

