"""
Unit tests for YFinanceProvider module.

Tests cover data fetching, rate limiting, symbol validation, and error handling
using mocked yfinance responses for fast and reliable testing.
"""

import pytest
import pandas as pd
import time
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from src.data.yfinance_provider import YFinanceProvider


class TestYFinanceProvider:
    """Test suite for YFinanceProvider class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.provider = YFinanceProvider(min_interval=0.1)  # Faster for testing
        
        # Create sample stock data for mocking
        dates = pd.date_range('2023-01-01', periods=30, freq='D')
        self.sample_data = pd.DataFrame({
            'Open': np.random.uniform(100, 110, 30),
            'High': np.random.uniform(105, 115, 30),
            'Low': np.random.uniform(95, 105, 30),
            'Close': np.random.uniform(100, 110, 30),
            'Volume': np.random.randint(1000000, 5000000, 30),
            'Dividends': np.zeros(30),
            'Stock Splits': np.zeros(30)
        }, index=dates)
        
        # Create insufficient data (less than 5 days)
        self.insufficient_data = self.sample_data.head(3)
        
        # Create empty data
        self.empty_data = pd.DataFrame()
    
    @patch('src.data.yfinance_provider.yf.Ticker')
    def test_fetch_stock_data_success(self, mock_ticker):
        """Test successful data fetching"""
        # Setup mock
        mock_instance = Mock()
        mock_instance.history.return_value = self.sample_data
        mock_ticker.return_value = mock_instance
        
        # Test
        result = self.provider.fetch_stock_data("AAPL", "1mo")
        
        # Assertions
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 30
        assert not result.empty
        mock_ticker.assert_called_once_with("AAPL")
        mock_instance.history.assert_called_once_with(period="1mo")
    
    @patch('src.data.yfinance_provider.yf.Ticker')
    def test_fetch_with_invalid_symbol_raises_error(self, mock_ticker):
        """Test handling of invalid symbols"""
        # Setup mock to return empty data
        mock_instance = Mock()
        mock_instance.history.return_value = self.empty_data
        mock_ticker.return_value = mock_instance
        
        # Test and assert - use a shorter symbol that passes length validation
        with pytest.raises(ValueError, match="No data found for symbol: FAKE"):
            self.provider.fetch_stock_data("FAKE", "1mo")
    
    @patch('src.data.yfinance_provider.yf.Ticker')
    def test_insufficient_data_handling(self, mock_ticker):
        """Test handling of insufficient data (less than 5 days)"""
        # Setup mock to return insufficient data
        mock_instance = Mock()
        mock_instance.history.return_value = self.insufficient_data
        mock_ticker.return_value = mock_instance
        
        # Test and assert
        with pytest.raises(ValueError, match="Insufficient data for AAPL: only 3 days available"):
            self.provider.fetch_stock_data("AAPL", "1d")
    
    @patch('src.data.yfinance_provider.yf.Ticker')
    @patch('src.data.yfinance_provider.time.sleep')
    def test_rate_limiting_delays_requests(self, mock_sleep, mock_ticker):
        """Test rate limiting behavior"""
        # Setup mock
        mock_instance = Mock()
        mock_instance.history.return_value = self.sample_data
        mock_ticker.return_value = mock_instance
        
        # Make two consecutive calls
        self.provider.fetch_stock_data("AAPL", "1mo")
        self.provider.fetch_stock_data("GOOGL", "1mo")
        
        # Assert sleep was called due to rate limiting
        mock_sleep.assert_called()
        assert mock_sleep.call_count >= 1
    
    @patch('src.data.yfinance_provider.yf.Ticker')
    def test_validate_symbol_accepts_valid_symbols(self, mock_ticker):
        """Test symbol validation with valid symbols"""
        # Setup mock to return valid data
        mock_instance = Mock()
        mock_instance.history.return_value = self.sample_data
        mock_ticker.return_value = mock_instance
        
        # Test valid symbols
        assert self.provider.validate_symbol("AAPL") is True
        assert self.provider.validate_symbol("googl") is True  # Should handle lowercase
        assert self.provider.validate_symbol(" MSFT ") is True  # Should handle whitespace
    
    @patch('src.data.yfinance_provider.yf.Ticker')
    def test_validate_symbol_rejects_invalid_symbols(self, mock_ticker):
        """Test symbol validation with invalid symbols"""
        # Setup mock to return empty data
        mock_instance = Mock()
        mock_instance.history.return_value = self.empty_data
        mock_ticker.return_value = mock_instance
        
        # Test invalid symbols - use shorter symbol that passes length validation
        assert self.provider.validate_symbol("FAKE") is False
        assert self.provider.validate_symbol("") is False  # Empty
        assert self.provider.validate_symbol("   ") is False  # Whitespace only
        
        # Test symbols that fail length validation
        assert self.provider.validate_symbol("TOOLONG") is False  # Too long
    
    @patch('src.data.yfinance_provider.yf.Ticker')
    def test_validate_symbol_handles_exceptions(self, mock_ticker):
        """Test symbol validation handles exceptions gracefully"""
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("API Error")
        
        # Should return False for any exception
        assert self.provider.validate_symbol("AAPL") is False
    
    def test_clean_symbol_validation(self):
        """Test symbol cleaning and validation"""
        # Valid symbols
        assert self.provider._clean_symbol("aapl") == "AAPL"
        assert self.provider._clean_symbol(" GOOGL ") == "GOOGL"
        assert self.provider._clean_symbol("BRK.A") == "BRK.A"
        
        # Invalid symbols should raise ValueError
        with pytest.raises(ValueError, match="Symbol must be a non-empty string"):
            self.provider._clean_symbol(None)
        
        with pytest.raises(ValueError, match="Symbol must be a non-empty string"):
            self.provider._clean_symbol("")
        
        with pytest.raises(ValueError, match="Symbol too long"):
            self.provider._clean_symbol("TOOLONG")
        
        with pytest.raises(ValueError, match="Invalid symbol format"):
            self.provider._clean_symbol("INVALID@")
    
    @patch('src.data.yfinance_provider.yf.Ticker')
    def test_fetch_stock_data_with_api_exception(self, mock_ticker):
        """Test handling of API exceptions"""
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("Network error")
        
        # Should raise ValueError with descriptive message
        with pytest.raises(ValueError, match="Failed to fetch data for AAPL"):
            self.provider.fetch_stock_data("AAPL", "1mo")
    
    @patch('src.data.yfinance_provider.time.time')
    def test_rate_limiting_timing(self, mock_time):
        """Test rate limiting timing calculations"""
        # Setup mock time sequence
        mock_time.side_effect = [0.0, 0.5, 1.0, 2.0]  # Sequence of time calls
        
        provider = YFinanceProvider(min_interval=1.0)
        
        # First call should not sleep (no previous call)
        provider._apply_rate_limiting()
        
        # Second call should sleep because only 0.5 seconds elapsed
        with patch('src.data.yfinance_provider.time.sleep') as mock_sleep:
            provider._apply_rate_limiting()
            mock_sleep.assert_called_once_with(0.5)  # Should sleep for remaining time
    
    def test_provider_initialization(self):
        """Test provider initialization with different parameters"""
        # Default initialization
        provider1 = YFinanceProvider()
        assert provider1.min_interval == 1.0
        assert provider1.last_call_time == 0
        
        # Custom initialization
        provider2 = YFinanceProvider(min_interval=2.0)
        assert provider2.min_interval == 2.0
        assert provider2.last_call_time == 0
    
    @patch('src.data.yfinance_provider.yf.Ticker')
    def test_symbol_case_handling(self, mock_ticker):
        """Test that symbols are properly converted to uppercase"""
        # Setup mock
        mock_instance = Mock()
        mock_instance.history.return_value = self.sample_data
        mock_ticker.return_value = mock_instance
        
        # Test with lowercase
        self.provider.fetch_stock_data("aapl", "1mo")
        
        # Assert ticker was called with uppercase symbol
        mock_ticker.assert_called_with("AAPL")
    
    @patch('src.data.yfinance_provider.yf.Ticker')
    def test_period_parameter_passing(self, mock_ticker):
        """Test that period parameter is correctly passed to yfinance"""
        # Setup mock
        mock_instance = Mock()
        mock_instance.history.return_value = self.sample_data
        mock_ticker.return_value = mock_instance
        
        # Test different periods
        periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y"]
        
        for period in periods:
            self.provider.fetch_stock_data("AAPL", period)
            mock_instance.history.assert_called_with(period=period)
    
    @patch('src.data.yfinance_provider.yf.Ticker')
    def test_data_frame_structure(self, mock_ticker):
        """Test that returned DataFrame has expected structure"""
        # Setup mock
        mock_instance = Mock()
        mock_instance.history.return_value = self.sample_data
        mock_ticker.return_value = mock_instance
        
        # Test
        result = self.provider.fetch_stock_data("AAPL", "1mo")
        
        # Assert DataFrame structure
        expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
        for col in expected_columns:
            assert col in result.columns
        
        assert len(result) > 0
        assert isinstance(result.index, pd.DatetimeIndex)
    
    @patch('src.data.yfinance_provider.yf.Ticker')
    def test_validate_symbol_rate_limiting(self, mock_ticker):
        """Test that validate_symbol also applies rate limiting"""
        # Setup mock
        mock_instance = Mock()
        mock_instance.history.return_value = self.sample_data
        mock_ticker.return_value = mock_instance
        
        with patch('src.data.yfinance_provider.time.sleep') as mock_sleep:
            # Make two validation calls quickly
            self.provider.validate_symbol("AAPL")
            self.provider.validate_symbol("GOOGL")
            
            # Assert sleep was called due to rate limiting
            assert mock_sleep.called
    
    def test_edge_cases_symbol_validation(self):
        """Test edge cases in symbol validation"""
        # Test with various invalid inputs
        invalid_symbols = [
            None,
            123,
            [],
            {},
            "",
            "   ",
            "SYMBOL!",
            "SYM@BOL",
            "TOOLONGNAME"
        ]
        
        for invalid_symbol in invalid_symbols:
            with pytest.raises(ValueError):
                self.provider._clean_symbol(invalid_symbol)
    
    @patch('src.data.yfinance_provider.yf.Ticker')
    def test_multiple_consecutive_calls_rate_limiting(self, mock_ticker):
        """Test rate limiting with multiple consecutive calls"""
        # Setup mock
        mock_instance = Mock()
        mock_instance.history.return_value = self.sample_data
        mock_ticker.return_value = mock_instance
        
        with patch('src.data.yfinance_provider.time.sleep') as mock_sleep:
            # Make multiple calls
            for symbol in ["AAPL", "GOOGL", "MSFT", "AMZN"]:
                self.provider.fetch_stock_data(symbol, "1mo")
            
            # Should have called sleep multiple times due to rate limiting
            assert mock_sleep.call_count >= 3  # Should sleep for most calls except first
