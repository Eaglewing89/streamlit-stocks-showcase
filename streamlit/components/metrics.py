"""
Key metrics display components for the Streamlit dashboard.

This module provides functions for displaying key financial metrics
using Streamlit's metric components with proper formatting.
"""

import streamlit as st
import pandas as pd
from utils.formatters import format_currency, format_volume, format_percentage, format_change


def render_key_metrics(indicators):
    """
    Render key financial metrics using st.metric components.
    
    Args:
        indicators: Dictionary containing technical indicators and price data
    """
    if not indicators:
        st.warning("⚠️ No metrics data available.")
        return
    
    try:
        st.subheader("📊 Key Metrics")
        
        # Create three columns for metrics
        col1, col2, col3 = st.columns(3)
        
        # Current Price with change
        current_price = indicators.get('current_price')
        price_change_1d = indicators.get('price_change_1d', {})
        
        if current_price is not None:
            with col1:
                change_amount = price_change_1d.get('amount', 0)
                change_percent = price_change_1d.get('percent', 0)
                delta_text = f"{change_amount:+.2f} ({change_percent:+.2f}%)" if change_amount != 0 else None
                
                st.metric(
                    label="💰 Current Price",
                    value=format_currency(current_price),
                    delta=delta_text
                )
        
        # Average Volume
        avg_volume = indicators.get('volume_avg')
        
        if avg_volume is not None:
            with col2:
                st.metric(
                    label="📈 Avg Volume (20d)",
                    value=format_volume(avg_volume)
                )
        
        # RSI
        rsi_value = indicators.get('rsi')
        if rsi_value is not None:
            with col3:
                # Determine RSI status for better visualization
                if rsi_value > 70:
                    rsi_status = "Overbought"
                elif rsi_value < 30:
                    rsi_status = "Oversold"
                else:
                    rsi_status = "Neutral"
                
                st.metric(
                    label=f"📉 RSI ({rsi_status})",
                    value=f"{rsi_value:.1f}",
                    help="RSI: >70 Overbought, <30 Oversold, 30-70 Neutral"
                )
        
        # Additional metrics row
        st.markdown("---")
        
        # Create additional metrics if available
        additional_metrics = []
        
        # Moving averages
        sma_20 = indicators.get('sma_20')
        sma_50 = indicators.get('sma_50')
        
        if sma_20 is not None and sma_50 is not None:
            additional_metrics.extend([
                ("📈 SMA 20", format_currency(sma_20)),
                ("📊 SMA 50", format_currency(sma_50))
            ])
        
        # Price changes
        price_change_5d = indicators.get('price_change_5d', {})
        if price_change_5d.get('percent') is not None:
            change_5d = price_change_5d.get('percent', 0)
            additional_metrics.append(("📈 5-Day Change", f"{change_5d:+.2f}%"))
        
        # Display additional metrics in columns
        if additional_metrics:
            num_metrics = len(additional_metrics)
            if num_metrics <= 4:
                cols = st.columns(num_metrics)
                for i, (label, value) in enumerate(additional_metrics):
                    with cols[i]:
                        st.metric(label=label, value=value)
            else:
                # Split into two rows if more than 4 metrics
                first_row = additional_metrics[:4]
                second_row = additional_metrics[4:]
                
                cols1 = st.columns(len(first_row))
                for i, (label, value) in enumerate(first_row):
                    with cols1[i]:
                        st.metric(label=label, value=value)
                
                if second_row:
                    cols2 = st.columns(len(second_row))
                    for i, (label, value) in enumerate(second_row):
                        with cols2[i]:
                            st.metric(label=label, value=value)
        
    except Exception as e:
        st.error(f"❌ Error rendering metrics: {str(e)}")


def render_price_metrics(stock_data):
    """
    Render price-specific metrics from stock data.
    
    Args:
        stock_data: DataFrame with OHLCV data
    """
    if stock_data is None or stock_data.empty:
        return
    
    try:
        st.subheader("💹 Price Metrics")
        
        latest_data = stock_data.iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🔼 High",
                value=format_currency(latest_data['High'])
            )
        
        with col2:
            st.metric(
                label="🔽 Low",
                value=format_currency(latest_data['Low'])
            )
        
        with col3:
            st.metric(
                label="🟢 Open",
                value=format_currency(latest_data['Open'])
            )
        
        with col4:
            st.metric(
                label="🔴 Close",
                value=format_currency(latest_data['Close'])
            )
            
    except Exception as e:
        st.error(f"❌ Error rendering price metrics: {str(e)}")


def render_trading_metrics(stock_data):
    """
    Render trading-specific metrics.
    
    Args:
        stock_data: DataFrame with OHLCV data
    """
    if stock_data is None or stock_data.empty:
        return
    
    try:
        st.subheader("📊 Trading Metrics")
        
        # Calculate some basic trading metrics
        latest_volume = stock_data['Volume'].iloc[-1]
        avg_volume = stock_data['Volume'].tail(20).mean()
        price_range = stock_data['High'].iloc[-1] - stock_data['Low'].iloc[-1]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="📈 Today's Volume",
                value=format_volume(latest_volume)
            )
        
        with col2:
            volume_change = (latest_volume - avg_volume) / avg_volume if avg_volume > 0 else 0
            st.metric(
                label="📊 Vol vs Avg",
                value=format_percentage(volume_change),
                delta=format_percentage(volume_change)
            )
        
        with col3:
            st.metric(
                label="📏 Today's Range",
                value=format_currency(price_range)
            )
            
    except Exception as e:
        st.error(f"❌ Error rendering trading metrics: {str(e)}")
