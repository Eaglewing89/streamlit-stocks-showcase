"""
Session management utilities for the Stock Dashboard.

This module handles Streamlit session state initialization and management,
ensuring consistent state across user interactions.
"""

import streamlit as st


def initialize_session():
    """
    Initialize session state with default values.
    
    Sets up default values for symbol, period, and language if they
    are not already initialized in the session state.
    """
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.symbol = ''
        st.session_state.period = '1mo'
        st.session_state.language = 'en'
        st.session_state.last_symbols = []
        st.session_state.preferences = {
            'chart_height': 600,
            'show_volume': True,
            'show_indicators': True
        }


def update_symbol_history(symbol):
    """
    Track recently viewed symbols in session state.
    
    Args:
        symbol (str): Stock symbol to add to history
    """
    if 'last_symbols' not in st.session_state:
        st.session_state.last_symbols = []
    
    if symbol and symbol not in st.session_state.last_symbols:
        st.session_state.last_symbols.insert(0, symbol)
        # Keep only last 5 symbols
        st.session_state.last_symbols = st.session_state.last_symbols[:5]
