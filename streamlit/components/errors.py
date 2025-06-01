"""
Error handling components for the Streamlit dashboard.

This module provides functions for displaying user-friendly error messages
and handling various types of analysis errors gracefully.
"""

import streamlit as st
import logging
import re
from ..config.ui_config import ERROR_MESSAGES, COLORS


def handle_analysis_error(error_object, symbol):
    """
    Display user-friendly error messages for analysis errors.
    
    Args:
        error_object: The exception object that was raised
        symbol: The stock symbol that caused the error
    """
    error_type = type(error_object).__name__
    error_message = str(error_object)
    
    # Log the error for debugging
    logging.error(f"Analysis error for symbol {symbol}: {error_type} - {error_message}")
    
    # Classify the error type
    classified_error = classify_error(error_message, error_type)
    
    # Display the classified error
    display_classified_error(classified_error, symbol, error_type, error_message)


def classify_error(error_message, error_type):
    """
    Classify the error based on message content and type.
    
    Args:
        error_message (str): The error message
        error_type (str): The error type name
    
    Returns:
        str: The classified error key
    """
    error_message_lower = error_message.lower()
    
    # Check for specific error patterns
    if any(pattern in error_message_lower for pattern in [
        "no data found", "invalid symbol", "not found", "ticker", "symbol"
    ]):
        return 'invalid_symbol'
    
    elif any(pattern in error_message_lower for pattern in [
        "api key", "authentication", "unauthorized", "forbidden"
    ]):
        return 'api_error'
    
    elif any(pattern in error_message_lower for pattern in [
        "network", "connection", "dns", "resolve", "unreachable"
    ]):
        return 'network_error'
    
    elif any(pattern in error_message_lower for pattern in [
        "rate limit", "too many requests", "quota exceeded"
    ]):
        return 'rate_limit'
    
    elif any(pattern in error_message_lower for pattern in [
        "timeout", "timed out", "time limit"
    ]):
        return 'timeout'
    
    elif any(pattern in error_message_lower for pattern in [
        "insufficient data", "not enough", "too few", "empty"
    ]):
        return 'insufficient_data'
    
    # Default to generic error
    return 'generic'


def display_classified_error(error_key, symbol, error_type, error_message):
    """
    Display a classified error with user-friendly messaging.
    
    Args:
        error_key (str): The classified error key
        symbol (str): The stock symbol
        error_type (str): The original error type
        error_message (str): The original error message
    """
    if error_key in ERROR_MESSAGES:
        error_config = ERROR_MESSAGES[error_key]
        
        # Display main error message
        title = error_config['title']
        message = error_config['message'].format(symbol=symbol) if '{symbol}' in error_config['message'] else error_config['message']
        
        st.error(f"❌ **{title}**: {message}")
        
        # Display suggestions
        if error_config['suggestions']:
            st.info("💡 **Suggestions:**")
            for suggestion in error_config['suggestions']:
                st.info(f"• {suggestion}")
    else:
        # Generic error fallback
        st.error(f"⚠️ **Analysis Error**: Unable to analyze '{symbol}' at this time.")
        st.warning("An unexpected error occurred. Please try again or contact support if the issue persists.")
    
    # Show technical details in an expander
    with st.expander("🔍 Technical Details", expanded=False):
        st.markdown(f"**Error Type:** `{error_type}`")
        st.markdown(f"**Error Message:** `{error_message}`")
        st.markdown(f"**Symbol:** `{symbol}`")


def display_error_card(title, message, suggestions=None, error_type="error"):
    """
    Display a styled error card with consistent formatting.
    
    Args:
        title (str): Error title
        message (str): Error message
        suggestions (list): List of suggestion strings
        error_type (str): Type of error for styling ('error', 'warning', 'info')
    """
    # Choose color and icon based on error type
    if error_type == "error":
        color = COLORS['danger']
        icon = "❌"
    elif error_type == "warning":
        color = COLORS['warning']
        icon = "⚠️"
    else:
        color = COLORS['primary']
        icon = "ℹ️"
    
    # Create styled error card
    st.markdown(
        f"""
        <div style="
            border: 2px solid {color}; 
            border-radius: 10px; 
            padding: 20px; 
            margin: 10px 0;
            background-color: {color}20;
        ">
            <h3 style="color: {color}; margin: 0 0 10px 0;">
                {icon} {title}
            </h3>
            <p style="margin: 0 0 15px 0; color: {COLORS['text']};">
                {message}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Display suggestions if provided
    if suggestions:
        st.info("💡 **What you can try:**")
        for suggestion in suggestions:
            st.info(f"• {suggestion}")


def show_validation_feedback(symbol, is_valid):
    """
    Show real-time validation feedback for stock symbols.
    
    Args:
        symbol (str): The stock symbol to validate
        is_valid (bool): Whether the symbol is valid
    """
    if not symbol:
        return
    
    if is_valid:
        st.success(f"✅ '{symbol}' appears to be a valid symbol")
    else:
        st.error(f"❌ '{symbol}' may not be a valid symbol")
        st.info("💡 Stock symbols are usually 1-5 uppercase letters (e.g., AAPL, GOOGL)")


def handle_insufficient_data_error(symbol, period):
    """
    Handle specific case of insufficient data for analysis.
    
    Args:
        symbol (str): The stock symbol
        period (str): The time period requested
    """
    error_config = ERROR_MESSAGES['insufficient_data']
    
    st.error(f"❌ **{error_config['title']}**: {error_config['message']}")
    st.warning(f"Not enough data available for **{symbol}** over the **{period}** period.")
    
    st.info("💡 **Suggestions:**")
    for suggestion in error_config['suggestions']:
        st.info(f"• {suggestion}")
    
    # Additional specific suggestions
    st.info("• Try popular symbols like AAPL, GOOGL, or MSFT")
    st.info("• Some symbols may have limited historical data")


def show_api_status_warning():
    """Show a warning about API status or limitations."""
    st.warning("⚠️ **API Status**: Some data sources may be experiencing delays.")
    st.info("💡 Data may be slightly delayed or limited during peak usage times.")


def show_demo_mode_info():
    """Show information about demo mode limitations."""
    st.info("🎯 **Demo Mode**: You're using the demo version with sample data.")
    st.markdown("""
    **Demo limitations:**
    • Limited to popular stock symbols
    • Data may be delayed or simulated
    • Some features may be restricted
    """)


def validate_and_suggest_symbol(symbol):
    """
    Validate a symbol and provide suggestions if invalid.
    
    Args:
        symbol (str): The stock symbol to validate
    
    Returns:
        dict: Validation result with suggestions
    """
    if not symbol:
        return {
            'valid': False,
            'message': 'Please enter a stock symbol',
            'suggestions': ['Try symbols like AAPL, GOOGL, MSFT']
        }
    
    # Basic format validation
    if not re.match(r'^[A-Z]{1,5}$', symbol.upper()):
        return {
            'valid': False,
            'message': f"'{symbol}' doesn't match typical symbol format",
            'suggestions': [
                'Use 1-5 uppercase letters (e.g., AAPL)',
                'Remove any numbers or special characters',
                'Check if you meant a similar symbol'
            ]
        }
    
    # If it looks valid
    return {
        'valid': True,
        'message': f"'{symbol}' appears to be a valid symbol format",
        'suggestions': []
    }


def handle_data_warning(message, symbol=None):
    """
    Display a warning message for data-related issues.
    
    Args:
        message: Warning message to display
        symbol: Optional stock symbol related to the warning
    """
    if symbol:
        st.warning(f"⚠️ **Data Warning for {symbol}**: {message}")
    else:
        st.warning(f"⚠️ **Data Warning**: {message}")


def handle_info_message(message, symbol=None):
    """
    Display an informational message.
    
    Args:
        message: Info message to display
        symbol: Optional stock symbol related to the message
    """
    if symbol:
        st.info(f"ℹ️ **{symbol}**: {message}")
    else:
        st.info(f"ℹ️ {message}")


def show_no_data_message():
    """Display a message when no analysis data is available."""
    st.info("👋 **Welcome to the Stock Dashboard!**")
    st.markdown("""
    📝 **Getting Started:**
    1. Enter a stock symbol in the sidebar (e.g., AAPL, GOOGL, MSFT)
    2. Select your preferred time period
    3. Choose your language preference
    4. Click 'Analyze' or press Enter to get started
    
    💡 **Popular symbols to try:** AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA
    """)


def show_loading_error():
    """Display a message when data loading fails."""
    st.error("❌ **Loading Failed**: Unable to load the analysis data.")
    st.info("Please try refreshing the page or selecting a different stock symbol.")
