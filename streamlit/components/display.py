"""
Display components for the Streamlit dashboard.

This module provides functions for displaying AI commentary,
technical summaries, and other analysis information with mobile responsiveness.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from utils.formatters import format_currency, format_percentage, format_number
from config.ui_config import COLORS, MOBILE_CONFIG


def render_ai_commentary(commentary_text):
    """
    Display AI-generated commentary in a styled block.
    
    Args:
        commentary_text: The AI-generated commentary text
    """
    if not commentary_text:
        st.warning("⚠️ No AI commentary available.")
        return
    
    try:
        st.subheader("🤖 AI Market Commentary")
        
        # Create a styled container for the commentary
        st.markdown(
            """
            <div style="
                background-color: #f0f2f6;
                border-left: 4px solid #1f77b4;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 1rem 0;
            ">
            """,
            unsafe_allow_html=True
        )
        
        # Display the commentary text
        st.markdown(commentary_text)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Add a small disclaimer
        st.caption("💡 This commentary is AI-generated and should not be considered as financial advice.")
        
    except Exception as e:
        st.error(f"❌ Error rendering AI commentary: {str(e)}")


def render_technical_summary(indicators):
    """
    Display technical indicators in a tabular format.
    
    Args:
        indicators: Dictionary containing technical indicators
    """
    if not indicators:
        st.warning("⚠️ No technical indicators available.")
        return
    
    try:
        st.subheader("📈 Technical Summary")
        
        # Prepare data for the summary table
        summary_data = []
        
        # Current Price
        current_price = indicators.get('current_price')
        if current_price is not None:
            summary_data.append({
                'Indicator': '💰 Current Price',
                'Value': format_currency(current_price),
                'Description': 'Latest trading price'
            })
        
        # Moving Averages
        sma_20 = indicators.get('sma_20')
        if sma_20 is not None:
            summary_data.append({
                'Indicator': '📈 SMA 20',
                'Value': format_currency(sma_20),
                'Description': '20-day Simple Moving Average'
            })
        
        sma_50 = indicators.get('sma_50')
        if sma_50 is not None:
            summary_data.append({
                'Indicator': '📊 SMA 50',
                'Value': format_currency(sma_50),
                'Description': '50-day Simple Moving Average'
            })
        
        # RSI
        rsi_current = indicators.get('rsi')
        if rsi_current is not None:
            rsi_interpretation = "Neutral"
            if rsi_current > 70:
                rsi_interpretation = "Overbought"
            elif rsi_current < 30:
                rsi_interpretation = "Oversold"
            
            summary_data.append({
                'Indicator': '📉 RSI',
                'Value': f"{rsi_current:.1f}",
                'Description': f'Relative Strength Index ({rsi_interpretation})'
            })
        
        # Trend Analysis
        trend = indicators.get('trend', 'Unknown')
        if trend != 'Unknown':
            trend_icon = '📈' if trend.lower() == 'bullish' else '📉' if trend.lower() == 'bearish' else '➡️'
            summary_data.append({
                'Indicator': f'{trend_icon} Trend',
                'Value': trend.capitalize(),
                'Description': 'Overall market trend direction'
            })
        
        # Volume Analysis
        avg_volume = indicators.get('volume_avg')
        if avg_volume is not None:
            summary_data.append({
                'Indicator': '📊 Avg Volume',
                'Value': format_number(avg_volume, 0),
                'Description': '20-day average trading volume'
            })
        
        # Price changes
        price_change_1d = indicators.get('price_change_1d', {})
        if price_change_1d.get('percent') is not None:
            change_1d = price_change_1d.get('percent', 0)
            summary_data.append({
                'Indicator': '📊 1-Day Change',
                'Value': f"{change_1d:+.2f}%",
                'Description': 'Price change from previous day'
            })
        
        price_change_5d = indicators.get('price_change_5d', {})
        if price_change_5d.get('percent') is not None:
            change_5d = price_change_5d.get('percent', 0)
            summary_data.append({
                'Indicator': '📊 5-Day Change',
                'Value': f"{change_5d:+.2f}%",
                'Description': 'Price change over 5 days'
            })
        
        # Display the summary table
        if summary_data:
            df = pd.DataFrame(summary_data)
            
            # Style the dataframe
            styled_df = df.style.apply(lambda x: ['background-color: #f0f2f6' if i % 2 == 0 else '' for i in range(len(x))], axis=0)
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("ℹ️ No technical indicators available for display.")
        
    except Exception as e:
        st.error(f"❌ Error rendering technical summary: {str(e)}")


def render_market_status(indicators):
    """
    Display market status and trading signals.
    
    Args:
        indicators: Dictionary containing technical indicators
    """
    try:
        st.subheader("🎯 Market Status")
        
        # Create columns for different status indicators
        col1, col2 = st.columns(2)
        
        with col1:
            # Trend status
            trend = indicators.get('trend', 'Unknown')
            if trend.lower() == 'bullish':
                st.success(f"📈 **Bullish Trend**")
            elif trend.lower() == 'bearish':
                st.error(f"📉 **Bearish Trend**")
            else:
                st.info(f"➡️ **Neutral/Sideways**")
        
        with col2:
            # RSI status
            rsi_current = indicators.get('rsi')
            if rsi_current is not None:
                if rsi_current > 70:
                    st.warning(f"⚠️ **Overbought** (RSI: {rsi_current:.1f})")
                elif rsi_current < 30:
                    st.success(f"💚 **Oversold** (RSI: {rsi_current:.1f})")
                else:
                    st.info(f"⚖️ **Neutral** (RSI: {rsi_current:.1f})")
        
        # Moving average analysis
        current_price = indicators.get('current_price')
        sma_20 = indicators.get('sma_20')
        sma_50 = indicators.get('sma_50')
        
        if all(x is not None for x in [current_price, sma_20, sma_50]):
            st.markdown("**📊 Moving Average Analysis:**")
            
            if current_price > sma_20 > sma_50:
                st.success("• Strong bullish signal: Price > SMA20 > SMA50")
            elif current_price < sma_20 < sma_50:
                st.error("• Strong bearish signal: Price < SMA20 < SMA50")
            elif current_price > sma_20:
                st.info("• Short-term bullish: Price above SMA20")
            elif current_price < sma_20:
                st.warning("• Short-term bearish: Price below SMA20")
            
    except Exception as e:
        st.error(f"❌ Error rendering market status: {str(e)}")


def render_data_info(analysis_data):
    """
    Display information about the analysis data.
    
    Args:
        analysis_data: The complete analysis data dictionary
    """
    try:
        with st.expander("ℹ️ Data Information"):
            symbol = analysis_data.get('symbol', 'Unknown')
            period = analysis_data.get('period', 'Unknown')
            last_updated = analysis_data.get('last_updated', 'Unknown')
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(label="Symbol", value=symbol)
            
            with col2:
                st.metric(label="Period", value=period.upper())
            
            with col3:
                st.metric(label="Last Updated", value=str(last_updated)[:19] if last_updated != 'Unknown' else 'Unknown')
            
            # Data quality indicators
            data = analysis_data.get('data')
            if data is not None and not data.empty:
                st.success(f"✅ Data Quality: {len(data)} data points available")
            else:
                st.warning("⚠️ Limited data available")
                
    except Exception as e:
        st.error(f"❌ Error rendering data info: {str(e)}")


def render_analysis_summary(analysis_data):
    """
    Render a comprehensive analysis summary.
    
    Args:
        analysis_data: The complete analysis data dictionary
    """
    try:
        indicators = analysis_data.get('indicators', {})
        
        # Market status
        render_market_status(indicators)
        
        st.markdown("---")
        
        # Technical summary
        render_technical_summary(indicators)
        
        st.markdown("---")
        
        # Data information
        render_data_info(analysis_data)
        
    except Exception as e:
        st.error(f"❌ Error rendering analysis summary: {str(e)}")


def render_last_updated_timestamp(timestamp=None, analysis_data=None):
    """
    Display the last updated timestamp prominently.
    
    Args:
        timestamp: Explicit timestamp to display
        analysis_data: Analysis data containing timestamp
    """
    try:
        # Try to get timestamp from various sources
        if timestamp:
            last_updated = timestamp
        elif analysis_data and 'last_updated' in analysis_data:
            last_updated = analysis_data['last_updated']
        elif analysis_data and 'metadata' in analysis_data and 'last_updated' in analysis_data['metadata']:
            last_updated = analysis_data['metadata']['last_updated']
        else:
            last_updated = datetime.now(timezone.utc)
        
        # Format timestamp
        if isinstance(last_updated, str):
            try:
                last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            except:
                last_updated = datetime.now(timezone.utc)
        
        # Format for display
        formatted_time = last_updated.strftime("%Y-%m-%d %H:%M:%S UTC")
        time_ago = get_time_ago_string(last_updated)
        
        # Create styled timestamp display
        st.markdown(
            f"""
            <div style="
                background-color: {COLORS['light_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px;
                margin: 10px 0;
                text-align: center;
            ">
                <div style="color: {COLORS['neutral']}; font-size: 14px; margin-bottom: 4px;">
                    📅 Last Updated
                </div>
                <div style="color: {COLORS['text']}; font-weight: bold; font-size: 16px;">
                    {formatted_time}
                </div>
                <div style="color: {COLORS['neutral']}; font-size: 12px;">
                    {time_ago}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    except Exception as e:
        st.caption(f"⏰ Last updated: {datetime.now().strftime('%H:%M:%S')}")


def get_time_ago_string(timestamp):
    """
    Get a human-readable time ago string.
    
    Args:
        timestamp: The timestamp to compare against now
    
    Returns:
        str: Time ago string
    """
    try:
        now = datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        
        diff = now - timestamp
        seconds = int(diff.total_seconds())
        
        if seconds < 60:
            return f"{seconds} seconds ago"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = seconds // 86400
            return f"{days} day{'s' if days != 1 else ''} ago"
    except:
        return "Recently"


def apply_mobile_responsive_layout():
    """
    Apply mobile-responsive CSS styles to the Streamlit app.
    """
    st.markdown(
        f"""
        <style>
        /* Mobile responsiveness */
        @media (max-width: 768px) {{
            .stApp > div:first-child {{
                padding-top: 1rem;
            }}
            
            .stMetric {{
                background-color: {COLORS['light_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 1rem;
                margin: 0.5rem 0;
            }}
            
            .stColumns > div {{
                padding: 0 0.5rem;
            }}
            
            .stDataFrame {{
                font-size: 12px;
            }}
            
            .stPlotlyChart {{
                margin: 0 -1rem;
            }}
            
            .stButton > button {{
                width: 100%;
                padding: 0.75rem;
                font-size: 16px;
                margin: 0.25rem 0;
            }}
            
            .stTextInput > div > div > input {{
                font-size: 16px;
                padding: 0.75rem;
            }}
            
            .stSelectbox > div > div > select {{
                font-size: 16px;
                padding: 0.75rem;
            }}
        }}
        
        /* Touch-friendly buttons */
        .stButton > button {{
            min-height: 44px;
            touch-action: manipulation;
        }}
        
        /* Improved readability */
        .stMarkdown {{
            line-height: 1.6;
        }}
        
        /* Better spacing on mobile */
        @media (max-width: 768px) {{
            .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def create_mobile_friendly_metrics(metrics_data, layout='horizontal'):
    """
    Create mobile-friendly metric displays.
    
    Args:
        metrics_data: Dictionary of metrics to display
        layout: 'horizontal' or 'vertical' layout
    """
    try:
        if not metrics_data:
            return
        
        # Check if mobile layout should be used
        if layout == 'vertical' or len(metrics_data) > 4:
            # Vertical layout for mobile or many metrics
            for label, value in metrics_data.items():
                create_metric_card(label, value)
        else:
            # Horizontal layout for desktop
            cols = st.columns(len(metrics_data))
            for i, (label, value) in enumerate(metrics_data.items()):
                with cols[i]:
                    create_metric_card(label, value)
                    
    except Exception as e:
        st.error(f"❌ Error creating metrics: {str(e)}")


def create_metric_card(label, value, delta=None):
    """
    Create a styled metric card.
    
    Args:
        label: The metric label
        value: The metric value
        delta: Optional delta value for change
    """
    try:
        # Format value if it's a number
        if isinstance(value, (int, float)):
            if abs(value) >= 1_000_000:
                formatted_value = f"{value/1_000_000:.2f}M"
            elif abs(value) >= 1_000:
                formatted_value = f"{value/1_000:.1f}K"
            else:
                formatted_value = f"{value:.2f}"
        else:
            formatted_value = str(value)
        
        # Create metric with or without delta
        if delta is not None:
            st.metric(label=label, value=formatted_value, delta=delta)
        else:
            st.metric(label=label, value=formatted_value)
            
    except Exception as e:
        st.write(f"**{label}**: {value}")


def render_responsive_data_table(data, title="Data Table"):
    """
    Render a responsive data table that works well on mobile.
    
    Args:
        data: DataFrame or list of dictionaries
        title: Table title
    """
    try:
        if data is None or (hasattr(data, 'empty') and data.empty):
            st.info("No data available")
            return
        
        # Convert to DataFrame if needed
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Mobile-friendly table display
        st.subheader(title)
        
        # Use container for better mobile display
        with st.container():
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
            
    except Exception as e:
        st.error(f"❌ Error rendering table: {str(e)}")


def show_mobile_navigation_hint():
    """Show navigation hints for mobile users."""
    st.markdown(
        """
        <div style="
            background-color: #e8f4f8;
            border: 1px solid #b3d9e8;
            border-radius: 6px;
            padding: 10px;
            margin: 10px 0;
            text-align: center;
            font-size: 14px;
        ">
            📱 <strong>Mobile Tip:</strong> Swipe left to access the sidebar menu
        </div>
        """,
        unsafe_allow_html=True
    )
