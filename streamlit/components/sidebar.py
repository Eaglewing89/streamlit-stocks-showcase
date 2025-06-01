"""
Sidebar controls component for the Stock Dashboard.

This module handles all sidebar UI controls including stock symbol input,
time period selection, language selection, and other user preferences.
"""

import streamlit as st
from config.ui_config import POPULAR_STOCKS, PERIOD_DISPLAY, LANGUAGE_DISPLAY, COLORS
from utils.validators import validate_stock_symbol, get_validation_icon


def format_period_display(period):
    """Convert period codes to user-friendly labels."""
    # Use the centralized PERIOD_DISPLAY configuration
    return PERIOD_DISPLAY.get(period, str(period))


def render_popular_stocks():
    """
    Render popular stock selection buttons.
    
    Returns:
        str or None: Selected stock symbol or None if no selection made
    """
    st.sidebar.markdown("### 🔥 Popular Stocks")
    st.sidebar.markdown("Click to analyze popular stocks:")
    
    selected_symbol = None
    
    for category, symbols in POPULAR_STOCKS.items():
        with st.sidebar.expander(f"📊 {category}", expanded=False):
            # Create columns for better layout
            cols = st.columns(2)
            for i, symbol in enumerate(symbols):
                col = cols[i % 2]
                if col.button(symbol, key=f"popular_{symbol}", use_container_width=True):
                    selected_symbol = symbol
    
    return selected_symbol


def render_symbol_input():
    """
    Render stock symbol input with real-time validation.
    
    Returns:
        tuple: (symbol, is_valid) - The entered symbol and its validation status
    """
    # Symbol input
    symbol = st.sidebar.text_input(
        "Stock Symbol",
        value=st.session_state.get('symbol', ''),
        placeholder="e.g., AAPL, GOOGL",
        help="Enter a valid stock ticker symbol",
        key="symbol_input"
    ).upper().strip()
    
    # Real-time validation feedback
    if symbol:
        validation = validate_stock_symbol(symbol)
        icon = get_validation_icon(validation['is_valid'])
        color = COLORS['success'] if validation['is_valid'] else COLORS['danger']
        
        st.sidebar.markdown(
            f"<div style='color: {color}; font-size: 0.9em; margin-top: -10px; margin-bottom: 10px;'>"
            f"{icon} {validation['message']}</div>",
            unsafe_allow_html=True
        )
        
        return symbol, validation['is_valid']
    
    return symbol, False


def render_controls():
    """
    Render sidebar controls and return user selections.
    
    Returns:
        tuple: (symbol, period, language) - User's current selections
    """
    # Sidebar title with custom styling
    st.sidebar.markdown(
        f"<h1 style='color: {COLORS['primary']}; text-align: center;'>📈 Stock Dashboard</h1>",
        unsafe_allow_html=True
    )
    
    # Add some space
    st.sidebar.markdown("---")
    
    # Check for popular stock selection first
    popular_selection = render_popular_stocks()
    if popular_selection:
        st.session_state.symbol = popular_selection
        st.rerun()
    
    # Add separator
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Manual Search")
    
    # Stock symbol input with validation
    symbol, is_valid = render_symbol_input()
    
    # Time period selection
    period = st.sidebar.selectbox(
        "Time Period",
        options=['1d', '5d', '1mo', '3mo', '6mo', '1y'],
        index=2,  # Default to '1mo'
        format_func=format_period_display,
        help="Select the time range for analysis"
    )
    
    # Language selection with improved styling
    st.sidebar.markdown("### 🌐 Language")
    language = st.sidebar.radio(
        "Choose your language:",
        options=['en', 'sv'],
        format_func=lambda x: LANGUAGE_DISPLAY.get(x, x),
        horizontal=True
    )
    
    # Recent symbols (if any)
    if 'recent_symbols' in st.session_state and st.session_state.recent_symbols:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🕒 Recent Symbols")
        recent_cols = st.sidebar.columns(len(st.session_state.recent_symbols[:3]))
        for i, recent_symbol in enumerate(st.session_state.recent_symbols[:3]):
            if recent_cols[i].button(recent_symbol, key=f"recent_{recent_symbol}"):
                st.session_state.symbol = recent_symbol
                st.rerun()
    
    # Update session state with current selections
    if symbol and is_valid:
        st.session_state.symbol = symbol
        # Add to recent symbols
        if 'recent_symbols' not in st.session_state:
            st.session_state.recent_symbols = []
        if symbol not in st.session_state.recent_symbols:
            st.session_state.recent_symbols.insert(0, symbol)
            st.session_state.recent_symbols = st.session_state.recent_symbols[:5]  # Keep only 5 recent
    
    st.session_state.period = period
    st.session_state.language = language
    
    # Display Controls Section
    render_display_controls()
    
    # Footer with tips
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<small>💡 **Tips:**<br>"
        "• Use popular stocks for quick analysis<br>"
        "• Symbol format: 1-5 letters (e.g., AAPL)<br>"
        "• Toggle sections above to customize your view</small>",
        unsafe_allow_html=True
    )
    
    return symbol, period, language


def render_display_controls():
    """
    Render display controls for toggling different sections of the analysis.
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎛️ Display Options")
    
    # Initialize display preferences if not set
    if 'display_prefs' not in st.session_state:
        st.session_state.display_prefs = {
            'show_price_charts': True,
            'show_technical_indicators': True,
            'show_metrics_analysis': True,
            'show_ai_commentary': True,
            'show_technical_summary': True
        }
    
    # Price Charts toggle
    st.session_state.display_prefs['show_price_charts'] = st.sidebar.checkbox(
        "📈 Price Charts",
        value=st.session_state.display_prefs['show_price_charts'],
        help="Show candlestick chart with moving averages and volume"
    )
    
    # Technical Indicators toggle
    st.session_state.display_prefs['show_technical_indicators'] = st.sidebar.checkbox(
        "📊 Technical Indicators",
        value=st.session_state.display_prefs['show_technical_indicators'],
        help="Show RSI gauge, trend indicators, and technical charts"
    )
    
    # Metrics & Analysis toggle
    st.session_state.display_prefs['show_metrics_analysis'] = st.sidebar.checkbox(
        "📋 Metrics & Analysis",
        value=st.session_state.display_prefs['show_metrics_analysis'],
        help="Show key metrics, price metrics, and market status"
    )
    
    # AI Commentary toggle
    st.session_state.display_prefs['show_ai_commentary'] = st.sidebar.checkbox(
        "🤖 AI Commentary",
        value=st.session_state.display_prefs['show_ai_commentary'],
        help="Show AI-generated market analysis and commentary"
    )
    
    # Technical Summary toggle
    st.session_state.display_prefs['show_technical_summary'] = st.sidebar.checkbox(
        "📑 Technical Summary",
        value=st.session_state.display_prefs['show_technical_summary'],
        help="Show detailed technical analysis summary table"
    )
    
    # Quick preset buttons
    st.sidebar.markdown("**Quick Presets:**")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("📊 All", key="preset_all", help="Show all sections"):
            st.session_state.display_prefs = {key: True for key in st.session_state.display_prefs}
            st.rerun()
    
    with col2:
        if st.button("🎯 Essential", key="preset_essential", help="Show only essential sections"):
            st.session_state.display_prefs = {
                'show_price_charts': True,
                'show_technical_indicators': True,
                'show_metrics_analysis': True,
                'show_ai_commentary': False,
                'show_technical_summary': False
            }
            st.rerun()


def get_display_preferences():
    """
    Get the current display preferences from session state.
    
    Returns:
        dict: Current display preferences
    """
    return st.session_state.get('display_prefs', {
        'show_price_charts': True,
        'show_technical_indicators': True,
        'show_metrics_analysis': True,
        'show_ai_commentary': True,
        'show_technical_summary': True
    })
