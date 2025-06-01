"""
UI Configuration constants for the Stock Dashboard.

This module contains all UI-related configuration constants including
chart settings, color schemes, layout configurations, and performance settings.
"""

# Chart configuration
CHART_CONFIG = {
    'height': 600,
    'template': 'plotly_white',
    'showlegend': True,
    'responsive': True,
    'margin': dict(l=0, r=0, t=50, b=0),
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'paper_bgcolor': 'rgba(0,0,0,0)'
}

# Professional color scheme for financial dashboard
COLORS = {
    'primary': '#1f77b4',      # Primary blue for main actions
    'success': '#2ca02c',      # Green for positive values/gains  
    'danger': '#d62728',       # Red for negative values/losses
    'warning': '#ff7f0e',      # Orange for warnings
    'neutral': '#7f7f7f',      # Gray for neutral/secondary text
    'background': '#ffffff',    # White background
    'text': '#262730',         # Dark text
    'light_bg': '#f0f2f6',     # Light background for cards
    'border': '#e1e5e9',       # Border color
    'grid': 'rgba(128,128,128,0.2)',  # Grid color for charts
    # Chart-specific colors
    'candlestick_up': '#00D4AA',     # Green for price increases
    'candlestick_down': '#FF6B6B',   # Red for price decreases
    'sma_20': '#FFA726',             # Orange for 20-day SMA
    'sma_50': '#AB47BC',             # Purple for 50-day SMA
    'rsi': '#2196F3',                # Blue for RSI line
    'volume': '#42A5F5'              # Light blue for volume
}

# Typography settings
TYPOGRAPHY = {
    'header_size': 20,
    'subheader_size': 16,
    'metric_size': 14,
    'body_size': 12,
    'font_family': 'Arial, sans-serif'
}

# Layout configuration
LAYOUT = {
    'sidebar_width': 300,
    'main_columns': [2, 1],  # Chart:Metrics ratio
    'metrics_columns': 3,
    'mobile_breakpoint': 768,
    'max_width': 1200,
    'padding': '1rem',
    'border_radius': '0.5rem'
}

# Performance settings
PERFORMANCE = {
    'cache_ttl': 300,  # 5 minutes
    'max_data_points': 1000,
    'lazy_load_threshold': 500,
    'spinner_delay': 0.5  # Delay before showing spinner
}

# Period display mappings
PERIOD_DISPLAY = {
    '1d': '1 Day',
    '5d': '5 Days', 
    '1mo': '1 Month',
    '3mo': '3 Months',
    '6mo': '6 Months',
    '1y': '1 Year'
}

# Language display mappings
LANGUAGE_DISPLAY = {
    'en': '🇺🇸 English',
    'sv': '🇸🇪 Svenska'
}

# Popular stock symbols for quick selection
POPULAR_STOCKS = {
    'Technology': ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'META'],
    'Finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
    'Healthcare': ['JNJ', 'PFE', 'UNH', 'MRK', 'ABBV'],
    'Consumer': ['AMZN', 'TSLA', 'NFLX', 'DIS', 'NKE']
}

# RSI interpretation settings
RSI_LEVELS = {
    'oversold': 30,
    'overbought': 70,
    'neutral': 50
}

# Trend indicator settings
TREND_INDICATORS = {
    'bullish': {'icon': '📈', 'color': COLORS['success'], 'label': 'Bullish'},
    'bearish': {'icon': '📉', 'color': COLORS['danger'], 'label': 'Bearish'},
    'neutral': {'icon': '➡️', 'color': COLORS['neutral'], 'label': 'Neutral'},
    'sideways': {'icon': '↔️', 'color': COLORS['warning'], 'label': 'Sideways'}
}

# Error message templates
ERROR_MESSAGES = {
    'invalid_symbol': {
        'title': 'Symbol Not Found',
        'message': "'{symbol}' is not a valid stock symbol or no data is available.",
        'suggestions': [
            'Check the spelling of the stock symbol',
            'Try a different symbol (e.g., AAPL, GOOGL, MSFT)',
            'Make sure the symbol is traded on a major exchange'
        ]
    },
    'api_error': {
        'title': 'API Configuration Error',
        'message': "There's an issue with the API configuration.",
        'suggestions': ['Please contact the administrator to resolve this issue.']
    },
    'network_error': {
        'title': 'Network Error',
        'message': 'Unable to fetch data due to connection issues.',
        'suggestions': [
            'Check your internet connection',
            'Try again in a few moments',
            'The data provider might be temporarily unavailable'
        ]
    },
    'rate_limit': {
        'title': 'Rate Limit Exceeded',
        'message': 'Too many requests have been made.',
        'suggestions': ['Please wait a moment before trying again.']
    },
    'timeout': {
        'title': 'Request Timeout',
        'message': 'The request took too long to complete.',
        'suggestions': [
            'Try again with a shorter time period',
            'Check your internet connection'
        ]
    },
    'insufficient_data': {
        'title': 'Insufficient Data',
        'message': 'Not enough data available for analysis.',
        'suggestions': [
            'Try a longer time period',
            'Check if the symbol is actively traded'
        ]
    }
}

# Default session state values
DEFAULT_SESSION_STATE = {
    'symbol': '',
    'period': '1mo',
    'language': 'en',
    'last_symbols': [],
    'preferences': {
        'chart_height': 600,
        'show_volume': True,
        'show_indicators': True,
        'theme': 'light'
    }
}

# Mobile responsive settings
MOBILE_CONFIG = {
    'sidebar_collapsed': True,
    'chart_height': 400,
    'metrics_layout': 'vertical',
    'touch_friendly': True
}
