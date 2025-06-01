"""
Display components for the Streamlit dashboard.

This module provides functions for displaying AI commentary,
technical summaries, and other analysis information.
"""

import streamlit as st
import pandas as pd
from utils.formatters import format_currency, format_percentage, format_number


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
