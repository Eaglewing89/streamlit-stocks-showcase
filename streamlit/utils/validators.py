"""
Validation utilities for the Stock Dashboard.

This module provides validation functions for user inputs,
particularly for stock symbols and other user-provided data.
"""

import re


def validate_stock_symbol(symbol):
    """
    Validate stock symbol format.
    
    Args:
        symbol (str): The stock symbol to validate
        
    Returns:
        dict: Validation result with 'is_valid' boolean and 'message' string
    """
    if not symbol:
        return {'is_valid': False, 'message': 'Symbol cannot be empty'}
    
    # Remove whitespace and convert to uppercase
    symbol = symbol.strip().upper()
    
    # Basic format validation
    if not re.match(r'^[A-Z]{1,5}$', symbol):
        return {
            'is_valid': False, 
            'message': 'Symbol must be 1-5 letters only'
        }
    
    # Check for common invalid patterns
    if len(symbol) < 1:
        return {'is_valid': False, 'message': 'Symbol too short'}
    
    if len(symbol) > 5:
        return {'is_valid': False, 'message': 'Symbol too long (max 5 characters)'}
    
    return {'is_valid': True, 'message': 'Valid symbol format'}


def get_validation_color(is_valid):
    """
    Get color for validation feedback.
    
    Args:
        is_valid (bool): Whether the input is valid
        
    Returns:
        str: Color code for the validation state
    """
    from ..config.ui_config import COLORS
    return COLORS['success'] if is_valid else COLORS['danger']


def get_validation_icon(is_valid):
    """
    Get icon for validation feedback.
    
    Args:
        is_valid (bool): Whether the input is valid
        
    Returns:
        str: Icon for the validation state
    """
    return "✅" if is_valid else "❌"
