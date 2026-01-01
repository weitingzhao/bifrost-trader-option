"""Option chain viewer with interactive charts."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="Option Chain Viewer",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Option Chain Viewer")

# Placeholder for database connection
# TODO: Connect to PostgreSQL database in Phase 2
st.info("⚠️ Database connection will be implemented in Phase 2. This is a placeholder UI.")

# Symbol selection
col1, col2 = st.columns(2)

with col1:
    selected_symbol = st.selectbox(
        "Select Symbol",
        options=["SPY", "QQQ", "AAPL", "MSFT", "TSLA"],
        index=0
    )

with col2:
    expiration_date = st.selectbox(
        "Expiration Date",
        options=["2024-01-19", "2024-02-16", "2024-03-15"],
        index=0
    )

# Display underlying price
st.metric("Underlying Price", "$0.00", "0.00%")

# Option Chain Visualization
st.subheader("Option Chain Visualization")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["Strike vs Price", "Greeks", "Volume/Open Interest"])

with tab1:
    st.markdown("### Strike Price vs Option Price")
    
    # Placeholder chart
    fig = go.Figure()
    
    # Call options
    fig.add_trace(go.Scatter(
        x=[],
        y=[],
        mode='lines+markers',
        name='Calls',
        line=dict(color='green', width=2),
        marker=dict(size=8)
    ))
    
    # Put options
    fig.add_trace(go.Scatter(
        x=[],
        y=[],
        mode='lines+markers',
        name='Puts',
        line=dict(color='red', width=2),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Option Prices by Strike",
        xaxis_title="Strike Price",
        yaxis_title="Option Price",
        hovermode='x unified',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### Greeks Visualization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Delta")
        fig_delta = go.Figure()
        fig_delta.add_trace(go.Scatter(
            x=[],
            y=[],
            mode='lines+markers',
            name='Delta',
            line=dict(color='blue', width=2)
        ))
        fig_delta.update_layout(
            title="Delta by Strike",
            xaxis_title="Strike Price",
            yaxis_title="Delta",
            height=300
        )
        st.plotly_chart(fig_delta, use_container_width=True)
    
    with col2:
        st.markdown("#### Gamma")
        fig_gamma = go.Figure()
        fig_gamma.add_trace(go.Scatter(
            x=[],
            y=[],
            mode='lines+markers',
            name='Gamma',
            line=dict(color='purple', width=2)
        ))
        fig_gamma.update_layout(
            title="Gamma by Strike",
            xaxis_title="Strike Price",
            yaxis_title="Gamma",
            height=300
        )
        st.plotly_chart(fig_gamma, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### Theta")
        fig_theta = go.Figure()
        fig_theta.add_trace(go.Scatter(
            x=[],
            y=[],
            mode='lines+markers',
            name='Theta',
            line=dict(color='orange', width=2)
        ))
        fig_theta.update_layout(
            title="Theta by Strike",
            xaxis_title="Strike Price",
            yaxis_title="Theta",
            height=300
        )
        st.plotly_chart(fig_theta, use_container_width=True)
    
    with col4:
        st.markdown("#### Vega")
        fig_vega = go.Figure()
        fig_vega.add_trace(go.Scatter(
            x=[],
            y=[],
            mode='lines+markers',
            name='Vega',
            line=dict(color='brown', width=2)
        ))
        fig_vega.update_layout(
            title="Vega by Strike",
            xaxis_title="Strike Price",
            yaxis_title="Vega",
            height=300
        )
        st.plotly_chart(fig_vega, use_container_width=True)

with tab3:
    st.markdown("### Volume and Open Interest")
    
    # Volume chart
    fig_volume = go.Figure()
    fig_volume.add_trace(go.Bar(
        x=[],
        y=[],
        name='Volume',
        marker_color='lightblue'
    ))
    fig_volume.update_layout(
        title="Volume by Strike",
        xaxis_title="Strike Price",
        yaxis_title="Volume",
        height=300
    )
    st.plotly_chart(fig_volume, use_container_width=True)
    
    # Open Interest chart
    fig_oi = go.Figure()
    fig_oi.add_trace(go.Bar(
        x=[],
        y=[],
        name='Open Interest',
        marker_color='lightcoral'
    ))
    fig_oi.update_layout(
        title="Open Interest by Strike",
        xaxis_title="Strike Price",
        yaxis_title="Open Interest",
        height=300
    )
    st.plotly_chart(fig_oi, use_container_width=True)

# Option Chain Table
st.subheader("Option Chain Data")

# Placeholder table
df = pd.DataFrame({
    'Strike': [],
    'Type': [],
    'Bid': [],
    'Ask': [],
    'Last': [],
    'Volume': [],
    'OI': [],
    'IV': [],
    'Delta': [],
    'Gamma': [],
    'Theta': [],
    'Vega': []
})

st.dataframe(df, use_container_width=True, hide_index=True)

st.info("💡 **Note**: This page will display real option chain data once the database is connected in Phase 2.")

