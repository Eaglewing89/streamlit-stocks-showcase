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
    'responsive': True
}

# Color scheme
COLORS = {
    'primary': '#1f77b4',
    'success': '#2ca02c', 
    'danger': '#d62728',
    'warning': '#ff7f0e',
    'neutral': '#7f7f7f',
    'background': '#ffffff',
    'text': '#262730'
}

# Layout configuration
LAYOUT = {
    'sidebar_width': 300,
    'main_columns': [2, 1],  # Chart:Metrics ratio
    'metrics_columns': 3,
    'mobile_breakpoint': 768
}

# Performance settings
PERFORMANCE = {
    'cache_ttl': 300,  # 5 minutes
    'max_data_points': 1000,
    'lazy_load_threshold': 500
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

# Default session state values
DEFAULT_SESSION_STATE = {
    'symbol': '',
    'period': '1mo',
    'language': 'en',
    'last_symbols': [],
    'preferences': {
        'chart_height': 600,
        'show_volume': True,
        'show_indicators': True
    }
}
