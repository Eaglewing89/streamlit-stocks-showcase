"""
YFinance Provider Module

Provides stock data fetching functionality using the yfinance library
with rate limiting and validation capabilities.
"""

import yfinance as yf
import pandas as pd
import time
from typing import Optional


class YFinanceProvider:
    """
    Simple Yahoo Finance data provider with basic rate limiting.
    
    This class provides methods to fetch historical stock data and validate
    stock symbols using the yfinance library. It includes basic rate limiting
    to avoid overwhelming the Yahoo Finance API.
    """
    
    def __init__(self, min_interval: float = 1.0):
        """
        Initialize the YFinanceProvider.
        
        Args:
            min_interval: Minimum interval in seconds between API calls (default: 1.0)
        """
        self.last_call_time = 0
        self.min_interval = min_interval
    
    def fetch_stock_data(self, symbol: str, period: str) -> pd.DataFrame:
        """
        Fetch stock data with simple rate limiting.
        
        Args:
            symbol: Stock symbol (e.g., "AAPL", "GOOGL")
            period: Time period (e.g., "1d", "5d", "1mo", "3mo", "6mo", "1y")
        
        Returns:
            DataFrame containing historical stock data with columns:
            Open, High, Low, Close, Volume, Dividends, Stock Splits
        
        Raises:
            ValueError: If symbol is invalid, no data found, or insufficient data
        """
        # Apply rate limiting
        self._apply_rate_limiting()
        
        # Validate and clean symbol
        symbol = self._clean_symbol(symbol)
        
        try:
            # Fetch data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                raise ValueError(f"No data found for symbol: {symbol}")
            
            # Validate data quality
            if len(data) < 5:  # Need minimum data for indicators
                raise ValueError(f"Insufficient data for {symbol}: only {len(data)} days available")
            
            return data
            
        except Exception as e:
            if isinstance(e, ValueError):
                raise  # Re-raise our custom ValueError messages
            raise ValueError(f"Failed to fetch data for {symbol}: {str(e)}")
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Quick symbol validation by attempting to fetch minimal data.
        
        Args:
            symbol: Stock symbol to validate
        
        Returns:
            True if symbol is valid and data is available, False otherwise
        """
        try:
            # Basic format validation
            symbol = self._clean_symbol(symbol)
            
            # Apply rate limiting
            self._apply_rate_limiting()
            
            # Try to fetch just one day of data for validation
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            return not data.empty
            
        except Exception:
            # Any exception during validation means invalid symbol
            return False
    
    def _apply_rate_limiting(self) -> None:
        """
        Apply rate limiting to prevent overwhelming the API.
        
        Ensures minimum interval between consecutive API calls.
        """
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        self.last_call_time = time.time()
    
    def _clean_symbol(self, symbol: str) -> str:
        """
        Clean and validate symbol format.
        
        Args:
            symbol: Raw symbol input
        
        Returns:
            Cleaned symbol in uppercase
        
        Raises:
            ValueError: If symbol format is invalid
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Symbol must be a non-empty string")
        
        # Clean and validate
        cleaned = symbol.upper().strip()
        
        if not cleaned:
            raise ValueError("Symbol cannot be empty")
        
        if len(cleaned) > 5:
            raise ValueError(f"Symbol too long: {cleaned} (max 5 characters)")
        
        # Basic alphanumeric validation (allow dots for some symbols like BRK.A)
        if not all(c.isalnum() or c == '.' for c in cleaned):
            raise ValueError(f"Invalid symbol format: {cleaned}")
        
        return cleaned
