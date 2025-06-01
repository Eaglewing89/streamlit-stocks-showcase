"""
Data formatting utilities for the Streamlit dashboard.

This module provides utility functions for formatting financial data
in a user-friendly way, including currency, volume, and percentage formatting.
"""

def format_currency(value, decimals=2):
    """
    Format a numeric value as currency.
    
    Args:
        value: Numeric value to format
        decimals: Number of decimal places (default: 2)
    
    Returns:
        Formatted currency string (e.g., $123.45)
    """
    if value is None:
        return "N/A"
    
    try:
        return f"${value:,.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"


def format_volume(volume):
    """
    Format trading volume in human-readable format.
    
    Args:
        volume: Volume value to format
    
    Returns:
        Formatted volume string (e.g., 1.2M, 10K)
    """
    if volume is None:
        return "N/A"
    
    try:
        volume = float(volume)
        
        if volume >= 1_000_000_000:
            return f"{volume / 1_000_000_000:.1f}B"
        elif volume >= 1_000_000:
            return f"{volume / 1_000_000:.1f}M"
        elif volume >= 1_000:
            return f"{volume / 1_000:.1f}K"
        else:
            return f"{volume:,.0f}"
    except (ValueError, TypeError):
        return "N/A"


def format_percentage(value, decimals=2, include_sign=True):
    """
    Format a value as percentage.
    
    Args:
        value: Numeric value to format (as decimal, e.g., 0.025 for 2.5%)
        decimals: Number of decimal places (default: 2)
        include_sign: Whether to include + for positive values (default: True)
    
    Returns:
        Formatted percentage string (e.g., +2.50%, -0.75%)
    """
    if value is None:
        return "N/A"
    
    try:
        percentage = value * 100
        
        if include_sign and percentage > 0:
            return f"+{percentage:.{decimals}f}%"
        else:
            return f"{percentage:.{decimals}f}%"
    except (ValueError, TypeError):
        return "N/A"


def format_number(value, decimals=2):
    """
    Format a numeric value with thousands separators.
    
    Args:
        value: Numeric value to format
        decimals: Number of decimal places (default: 2)
    
    Returns:
        Formatted number string (e.g., 1,234.56)
    """
    if value is None:
        return "N/A"
    
    try:
        return f"{value:,.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"


def format_change(current_value, previous_value, as_percentage=True, decimals=2):
    """
    Calculate and format the change between two values.
    
    Args:
        current_value: Current value
        previous_value: Previous value
        as_percentage: Whether to format as percentage (default: True)
        decimals: Number of decimal places (default: 2)
    
    Returns:
        Tuple of (absolute_change, formatted_change_string)
    """
    if current_value is None or previous_value is None:
        return None, "N/A"
    
    try:
        absolute_change = current_value - previous_value
        
        if as_percentage and previous_value != 0:
            percentage_change = absolute_change / previous_value
            return absolute_change, format_percentage(percentage_change, decimals)
        else:
            return absolute_change, format_currency(absolute_change, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return None, "N/A"
