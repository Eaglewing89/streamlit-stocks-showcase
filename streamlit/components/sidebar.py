"""
Sidebar controls component for the Stock Dashboard.

This module handles all sidebar UI controls including stock symbol input,
time period selection, language selection, and other user preferences.
"""

import streamlit as st


def format_period_display(period):
    """Convert period codes to user-friendly labels."""
    periods = {
        '1d': '1 Day',
        '5d': '5 Days', 
        '1mo': '1 Month',
        '3mo': '3 Months',
        '6mo': '6 Months',
        '1y': '1 Year'
    }
    # Ensure we always return a string, never None
    return periods.get(period, str(period))


def render_controls():
    """
    Render sidebar controls and return user selections.
    
    Returns:
        tuple: (symbol, period, language) - User's current selections
    """
    # Sidebar title
    st.sidebar.title("📈 Stock Dashboard")
    
    # Stock symbol input
    symbol = st.sidebar.text_input(
        "Stock Symbol",
        value=st.session_state.get('symbol', ''),
        placeholder="e.g., AAPL, GOOGL",
        help="Enter a valid stock ticker symbol"
    ).upper()
    
    # Time period selection
    period = st.sidebar.selectbox(
        "Time Period",
        options=['1d', '5d', '1mo', '3mo', '6mo', '1y'],
        index=2,  # Default to '1mo'
        format_func=format_period_display
    )
    
    # Language selection
    language = st.sidebar.radio(
        "Language",
        options=['en', 'sv'],
        format_func=lambda x: '🇺🇸 English' if x == 'en' else '🇸🇪 Svenska'
    )
    
    # Update session state with current selections
    if symbol:
        st.session_state.symbol = symbol
    st.session_state.period = period
    st.session_state.language = language
    
    return symbol, period, language
