"""
Chart visualization components for the Streamlit dashboard.

This module provides functions for rendering interactive financial charts
using Plotly, including candlestick charts, moving averages, and volume charts.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from utils.formatters import format_currency, format_volume


def render_price_chart(stock_data, indicators):
    """
    Render an interactive price chart with candlesticks, moving averages, and volume.
    
    Args:
        stock_data: DataFrame with OHLCV data (Open, High, Low, Close, Volume)
        indicators: Dictionary containing technical indicators including SMAs
    """
    if stock_data is None or stock_data.empty:
        st.warning("⚠️ No price data available for chart.")
        return
    
    try:
        # Create subplots with secondary y-axis for volume
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('Price & Moving Averages', 'Volume'),
            row_width=[0.7, 0.3]
        )
        
        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=stock_data.index,
                open=stock_data['Open'],
                high=stock_data['High'],
                low=stock_data['Low'],
                close=stock_data['Close'],
                name="Price",
                increasing_line_color='#00D4AA',
                decreasing_line_color='#FF6B6B'
            ),
            row=1, col=1
        )
        
        # Add moving averages if available
        # Since backend only returns latest values, we'll calculate the series for plotting
        close_prices = stock_data['Close']
        
        if indicators and 'sma_20' in indicators and indicators['sma_20'] is not None:
            # Calculate SMA 20 series for plotting
            sma_20_series = close_prices.rolling(window=20).mean()
            if not sma_20_series.isna().all():
                fig.add_trace(
                    go.Scatter(
                        x=sma_20_series.index,
                        y=sma_20_series.values,
                        mode='lines',
                        name='SMA 20',
                        line=dict(color='#FFA726', width=2)
                    ),
                    row=1, col=1
                )
        
        if indicators and 'sma_50' in indicators and indicators['sma_50'] is not None:
            # Calculate SMA 50 series for plotting
            sma_50_series = close_prices.rolling(window=50).mean()
            if not sma_50_series.isna().all():
                fig.add_trace(
                    go.Scatter(
                        x=sma_50_series.index,
                        y=sma_50_series.values,
                        mode='lines',
                        name='SMA 50',
                        line=dict(color='#AB47BC', width=2)
                    ),
                    row=1, col=1
                )
        
        # Add volume chart
        colors = ['#00D4AA' if close >= open_price else '#FF6B6B' 
                 for close, open_price in zip(stock_data['Close'], stock_data['Open'])]
        
        fig.add_trace(
            go.Bar(
                x=stock_data.index,
                y=stock_data['Volume'],
                name="Volume",
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': "Stock Price Analysis",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_rangeslider_visible=False,
            height=600,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=0, r=0, t=50, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        # Update x-axis
        fig.update_xaxes(
            title_text="Date",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            row=2, col=1
        )
        
        # Update y-axes
        fig.update_yaxes(
            title_text="Price ($)",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            row=1, col=1
        )
        
        fig.update_yaxes(
            title_text="Volume",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            row=2, col=1
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error rendering price chart: {str(e)}")


def render_indicators_chart(indicators, stock_data=None):
    """
    Render a chart showing technical indicators like RSI.
    
    Args:
        indicators: Dictionary containing technical indicators
        stock_data: DataFrame with stock data (needed for RSI calculation)
    """
    if not indicators:
        return
    
    try:
        # Check if we have RSI data to display and stock data to calculate series
        if 'rsi' in indicators and indicators['rsi'] is not None and stock_data is not None:
            close_prices = stock_data['Close']
            
            # Calculate RSI series for plotting (replicating backend calculation)
            delta = close_prices.diff()
            gains = delta.clip(lower=0.0)
            losses = (-delta).clip(lower=0.0)
            
            gain = gains.rolling(window=14).mean()
            loss = losses.rolling(window=14).mean()
            
            # Calculate RSI series
            rs = gain / loss
            rsi_series = 100 - (100 / (1 + rs))
            
            # Only plot if we have valid data
            if not rsi_series.isna().all():
                fig = go.Figure()
                
                # Add RSI line
                fig.add_trace(
                    go.Scatter(
                        x=rsi_series.index,
                        y=rsi_series.values,
                        mode='lines',
                        name='RSI',
                        line=dict(color='#2196F3', width=2)
                    )
                )
                
                # Add overbought/oversold lines
                fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
                fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
                fig.add_hline(y=50, line_dash="dot", line_color="gray", annotation_text="Neutral (50)")
                
                # Update layout
                fig.update_layout(
                    title={
                        'text': "Relative Strength Index (RSI)",
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 16}
                    },
                    height=300,
                    xaxis_title="Date",
                    yaxis_title="RSI",
                    yaxis=dict(range=[0, 100]),
                    showlegend=False,
                    margin=dict(l=0, r=0, t=50, b=0),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                # Update grid
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
                
                st.plotly_chart(fig, use_container_width=True)
                
    except Exception as e:
        st.error(f"❌ Error rendering indicators chart: {str(e)}")


def create_mini_chart(data, title="", height=150):
    """
    Create a small chart for use in metrics or summary sections.
    
    Args:
        data: Time series data to plot
        title: Chart title
        height: Chart height in pixels
    
    Returns:
        Plotly figure object
    """
    if data is None or len(data) == 0:
        return None
    
    try:
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=list(range(len(data))),
                y=data,
                mode='lines',
                line=dict(color='#2196F3', width=2),
                showlegend=False
            )
        )
        
        fig.update_layout(
            title=title,
            height=height,
            margin=dict(l=0, r=0, t=30, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False)
        )
        
        return fig
        
    except Exception as e:
        st.error(f"❌ Error creating mini chart: {str(e)}")
        return None
