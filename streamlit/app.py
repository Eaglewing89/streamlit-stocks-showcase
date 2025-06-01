"""
Main Streamlit application file for the Stock Dashboard.

This serves as the primary entry point for the Streamlit application,
handling page configuration, session management, component orchestration,
and backend integration.
"""

import streamlit as st
import sys
import os

# Add the parent directory to the Python path for package imports
parent_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(parent_path)

from utils.session import initialize_session
from components.sidebar import render_controls, get_display_preferences
from components.charts import render_price_chart, render_indicators_chart, render_rsi_gauge, render_trend_indicator
from components.display import (
    render_ai_commentary, render_analysis_summary, render_last_updated_timestamp,
    apply_mobile_responsive_layout, show_mobile_navigation_hint
)
from components.metrics import render_key_metrics, render_price_metrics
from components.errors import handle_analysis_error, show_no_data_message
from src.dashboard import StockDashboard
from config.ui_config import PERFORMANCE


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
    Render the complete stock analysis with loading indicators and enhanced UI.
    
    Args:
        dashboard: StockDashboard instance
        symbol: Stock symbol
        period: Time period
        language: Language preference
    """
    try:
        # Show loading spinner with custom messages
        loading_messages = [
            f"🔍 Fetching {symbol} data...",
            "📊 Calculating technical indicators...",
            "🤖 Generating AI commentary...",
            "✨ Finalizing analysis..."
        ]
        
        # Get analysis data with enhanced loading feedback
        with st.spinner("🔄 Analyzing stock data..."):
            # Add a small delay to show spinner for better UX
            import time
            time.sleep(PERFORMANCE.get('spinner_delay', 0.5))
            
            analysis = dashboard.get_stock_analysis(symbol, period, language)
        
        # Get display preferences
        display_prefs = get_display_preferences()
        
        # Display last updated timestamp prominently at the top
        render_last_updated_timestamp(analysis_data=analysis)
        
        # Extract data components
        stock_data = analysis.get('data')
        indicators = analysis.get('indicators', {})
        commentary = analysis.get('commentary', '')
        
        # Check if we have valid data
        if stock_data is None or stock_data.empty:
            st.warning("⚠️ No data available for the selected symbol and period.")
            return
        
        # Enhanced trend indicator at the top (if technical indicators are enabled)
        if display_prefs.get('show_technical_indicators', True):
            with st.container():
                st.markdown("### 🎯 Market Overview")
                render_trend_indicator(stock_data, indicators)
            st.markdown("---")
        
        # Create responsive layout
        # On mobile, stack vertically; on desktop, use columns
        is_mobile = st.session_state.get('is_mobile', False)
        
        if is_mobile:
            # Mobile layout - vertical stacking
            render_mobile_layout(stock_data, indicators, commentary, analysis, display_prefs)
        else:
            # Desktop layout - columns
            render_desktop_layout(stock_data, indicators, commentary, analysis, display_prefs)
        
    except Exception as e:
        handle_analysis_error(e, symbol)


def render_desktop_layout(stock_data, indicators, commentary, analysis, display_prefs):
    """Render desktop layout with columns based on display preferences."""
    # Create main layout with two columns
    col1, col2 = st.columns([2, 1])
    
    # Left column - Charts
    with col1:
        # Price Charts section
        if display_prefs.get('show_price_charts', True):
            st.markdown("### 📊 Price Analysis")
            with st.spinner("📈 Rendering price chart..."):
                render_price_chart(stock_data, indicators)
        
        # Technical Indicators Chart section
        if display_prefs.get('show_technical_indicators', True) and indicators and 'rsi' in indicators:
            st.markdown("### 📉 Technical Indicators")
            with st.spinner("📊 Rendering technical indicators..."):
                render_indicators_chart(indicators, stock_data)
    
    # Right column - Metrics and Commentary
    with col2:
        # Technical Indicators - RSI Gauge
        if display_prefs.get('show_technical_indicators', True) and indicators and 'rsi' in indicators:
            st.markdown("### ⚖️ RSI Gauge")
            render_rsi_gauge(indicators['rsi'])
            st.markdown("---")
        
        # Metrics & Analysis section
        if display_prefs.get('show_metrics_analysis', True):
            st.markdown("### 📊 Key Metrics")
            render_key_metrics(indicators, show_title=False)
            
            st.markdown("---")
            
            # Additional price metrics
            if stock_data is not None and not stock_data.empty:
                st.markdown("### 💰 Price Metrics")
                render_price_metrics(stock_data, show_title=False)
                st.markdown("---")
        
        # AI Commentary section
        if display_prefs.get('show_ai_commentary', True) and commentary:
            st.markdown("### 🤖 AI Analysis")
            render_ai_commentary(commentary, show_title=False)
            st.markdown("---")
    
    # Full-width sections at the bottom
    # Technical Summary section
    if display_prefs.get('show_technical_summary', True):
        with st.spinner("📋 Preparing analysis summary..."):
            render_analysis_summary(analysis)


def render_mobile_layout(stock_data, indicators, commentary, analysis, display_prefs):
    """Render mobile-friendly vertical layout based on display preferences."""
    
    # Technical Indicators - RSI Gauge first (if available and enabled)
    if display_prefs.get('show_technical_indicators', True) and indicators and 'rsi' in indicators:
        st.markdown("### ⚖️ RSI Gauge")
        render_rsi_gauge(indicators['rsi'])
        st.markdown("---")
    
    # Metrics & Analysis section
    if display_prefs.get('show_metrics_analysis', True):
        st.markdown("### 📊 Key Metrics")
        render_key_metrics(indicators, show_title=False)
        st.markdown("---")
    
    # Price Charts section
    if display_prefs.get('show_price_charts', True):
        st.markdown("### 📊 Price Analysis")
        with st.spinner("📈 Loading chart..."):
            render_price_chart(stock_data, indicators)
    
    # Technical Indicators Chart section
    if display_prefs.get('show_technical_indicators', True) and indicators and 'rsi' in indicators:
        st.markdown("### 📉 Technical Indicators")
        with st.spinner("📊 Loading indicators..."):
            render_indicators_chart(indicators, stock_data)
    
    # Metrics & Analysis - Price metrics
    if display_prefs.get('show_metrics_analysis', True) and stock_data is not None and not stock_data.empty:
        st.markdown("### 💰 Price Metrics")
        render_price_metrics(stock_data, show_title=False)
    
    # AI Commentary section
    if display_prefs.get('show_ai_commentary', True) and commentary:
        st.markdown("### 🤖 AI Analysis")
        render_ai_commentary(commentary, show_title=False)
        st.markdown("### 🤖 AI Analysis")
        render_ai_commentary(commentary, show_title=False)
    
    # Technical Summary section
    if display_prefs.get('show_technical_summary', True):
        st.markdown("---")
        with st.spinner("📋 Loading summary..."):
            render_analysis_summary(analysis)


def render_welcome_screen():
    """Render the welcome screen when no symbol is selected."""
    show_no_data_message()


def main():
    """Main application function with enhanced mobile support."""
    # Page configuration
    st.set_page_config(
        page_title="Stock Dashboard",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/your-repo/stock-dashboard',
            'Report a bug': 'https://github.com/your-repo/stock-dashboard/issues',
            'About': '# Stock Dashboard\nA professional financial analysis tool powered by AI.'
        }
    )
    
    # Apply mobile responsiveness
    apply_mobile_responsive_layout()
    
    # Initialize session state
    initialize_session()
    
    # Detect mobile (simplified detection)
    # In a real app, you might use JavaScript for more accurate detection
    if 'is_mobile' not in st.session_state:
        st.session_state.is_mobile = False
    
    # Get dashboard instance
    with st.spinner("🚀 Initializing dashboard..."):
        dashboard = get_dashboard_instance()
    
    # Render sidebar controls and get user selections
    symbol, period, language = render_controls()
    
    # Main page content
    st.title("📈 Stock Dashboard")
    
    # Show mobile navigation hint on smaller screens
    if st.session_state.get('is_mobile', False):
        show_mobile_navigation_hint()
    
    # Main content area
    if symbol:
        # Display current selections with enhanced styling
        with st.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"📊 **Symbol:** {symbol}")
            with col2:
                st.info(f"⏰ **Period:** {period.upper()}")
            with col3:
                st.info(f"🌐 **Language:** {'English' if language == 'en' else 'Swedish'}")
        
        st.markdown("---")
        
        # Render analysis with loading indicators
        render_analysis(dashboard, symbol, period, language)
    else:
        # Welcome screen
        render_welcome_screen()
    
    # Footer with additional info
    with st.container():
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                """
                <div style='text-align: center; color: #666; font-size: 12px; padding: 20px;'>
                    📈 Stock Dashboard • Powered by AI • Real-time Financial Analysis<br>
                    <em>Data provided by Yahoo Finance • Analysis is for educational purposes only</em>
                </div>
                """,
                unsafe_allow_html=True
            )


if __name__ == "__main__":
    main()
