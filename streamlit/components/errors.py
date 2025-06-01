"""
Error handling components for the Streamlit dashboard.

This module provides functions for displaying user-friendly error messages
and handling various types of analysis errors gracefully.
"""

import streamlit as st
import logging


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
    
    # Handle specific error types with user-friendly messages
    if "No data found" in error_message.lower() or "invalid symbol" in error_message.lower():
        st.error(f"❌ **Symbol Not Found**: '{symbol}' is not a valid stock symbol or no data is available.")
        st.info("💡 **Tips:**")
        st.info("• Check the spelling of the stock symbol")
        st.info("• Try a different symbol (e.g., AAPL, GOOGL, MSFT)")
        st.info("• Make sure the symbol is traded on a major exchange")
        
    elif "api key" in error_message.lower() or "authentication" in error_message.lower():
        st.error("🔑 **API Configuration Error**: There's an issue with the API configuration.")
        st.warning("Please contact the administrator to resolve this issue.")
        
    elif "network" in error_message.lower() or "connection" in error_message.lower():
        st.error("🌐 **Network Error**: Unable to fetch data due to connection issues.")
        st.info("💡 **Tips:**")
        st.info("• Check your internet connection")
        st.info("• Try again in a few moments")
        st.info("• The data provider might be temporarily unavailable")
        
    elif "rate limit" in error_message.lower() or "too many requests" in error_message.lower():
        st.error("⏱️ **Rate Limit Exceeded**: Too many requests have been made.")
        st.warning("Please wait a moment before trying again.")
        
    elif "timeout" in error_message.lower():
        st.error("⏰ **Request Timeout**: The request took too long to complete.")
        st.info("💡 **Tips:**")
        st.info("• Try again with a shorter time period")
        st.info("• Check your internet connection")
        
    else:
        # Generic error message for unknown errors
        st.error(f"⚠️ **Analysis Error**: Unable to analyze '{symbol}' at this time.")
        st.warning("An unexpected error occurred. Please try again or contact support if the issue persists.")
        
        # Show technical details in an expander for debugging
        with st.expander("🔍 Technical Details"):
            st.code(f"Error Type: {error_type}")
            st.code(f"Error Message: {error_message}")


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
