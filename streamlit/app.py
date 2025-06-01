"""
Main Streamlit application file for the Stock Dashboard.

This serves as the primary entry point for the Streamlit application,
handling page configuration, session management, component orchestration,
and backend integration.
"""

import streamlit as st
import sys
import os

# Add the src directory to the Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.session import initialize_session
from components.sidebar import render_controls
from components.charts import render_price_chart, render_indicators_chart
from components.display import render_ai_commentary, render_analysis_summary
from components.metrics import render_key_metrics, render_price_metrics
from components.errors import handle_analysis_error, show_no_data_message
from src.dashboard import StockDashboard


@st.cache_resource
def get_dashboard_instance():
    """Get a cached instance of the StockDashboard."""
    try:
        return StockDashboard()
    except Exception as e:
        st.error(f"❌ Failed to initialize dashboard: {str(e)}")
        st.stop()


def render_analysis(dashboard, symbol, period, language):
    """
    Render the complete stock analysis.
    
    Args:
        dashboard: StockDashboard instance
        symbol: Stock symbol
        period: Time period
        language: Language preference
    """
    try:
        # Get analysis data with caching
        with st.spinner("🔄 Fetching and analyzing data..."):
            analysis = dashboard.get_stock_analysis(symbol, period, language)
        
        # Extract data components
        stock_data = analysis.get('data')
        indicators = analysis.get('indicators', {})
        commentary = analysis.get('commentary', '')
        
        # Create main layout with two columns
        col1, col2 = st.columns([2, 1])
        
        # Left column - Charts
        with col1:
            st.markdown("### 📊 Price Analysis")
            render_price_chart(stock_data, indicators)
            
            # Additional indicators chart if RSI data is available
            if indicators and 'rsi' in indicators:
                render_indicators_chart(indicators, stock_data)
        
        # Right column - Metrics and Commentary
        with col2:
            # Key metrics
            render_key_metrics(indicators)
            
            st.markdown("---")
            
            # AI Commentary
            if commentary:
                render_ai_commentary(commentary)
            
            st.markdown("---")
            
            # Additional price metrics
            if stock_data is not None and not stock_data.empty:
                render_price_metrics(stock_data)
        
        # Full-width analysis summary at the bottom
        st.markdown("---")
        render_analysis_summary(analysis)
        
    except Exception as e:
        handle_analysis_error(e, symbol)


def render_welcome_screen():
    """Render the welcome screen when no symbol is selected."""
    show_no_data_message()


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
    
    # Get dashboard instance
    dashboard = get_dashboard_instance()
    
    # Render sidebar controls and get user selections
    symbol, period, language = render_controls()
    
    # Main page content
    st.title("📈 Stock Dashboard")
    
    # Main content area
    if symbol:
        # Display current selections
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"📊 **Symbol:** {symbol}")
        with col2:
            st.info(f"⏰ **Period:** {period.upper()}")
        with col3:
            st.info(f"🌐 **Language:** {'English' if language == 'en' else 'Swedish'}")
        
        st.markdown("---")
        
        # Render analysis
        render_analysis(dashboard, symbol, period, language)
    else:
        # Welcome screen
        render_welcome_screen()


if __name__ == "__main__":
    main()
