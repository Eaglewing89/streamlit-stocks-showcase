"""
Main Streamlit application file for the Stock Dashboard.

This serves as the primary entry point for the Streamlit application,
handling page configuration, session management, and component orchestration.
"""

import streamlit as st
from utils.session import initialize_session
from components.sidebar import render_controls


def main():
    """Main application function."""
    # Page configuration
    st.set_page_config(
        page_title="Stock Dashboard",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session()
    
    # Render sidebar controls and get user selections
    symbol, period, language = render_controls()
    
    # Main page content
    st.title("📈 Stock Dashboard")
    
    # Temporarily display selections for testing
    if symbol:
        st.success(f"Selected Symbol: **{symbol}**")
        st.info(f"Selected Period: **{period}**")
        st.info(f"Selected Language: **{language}**")
        
        # Placeholder for future analysis content
        st.write("📊 Analysis content will be displayed here in future issues.")
    else:
        st.write("👋 Welcome to the Stock Dashboard!")
        st.write("📝 Please enter a stock symbol in the sidebar to get started.")


if __name__ == "__main__":
    main()
