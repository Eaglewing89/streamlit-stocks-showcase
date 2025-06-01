"""
Integration tests for the full stock analysis workflow.

These tests verify that all components work together correctly while
mocking only the external API calls (yfinance and OpenAI).
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.dashboard import StockDashboard
from src.config import Config


@pytest.fixture
def test_config():
    """Create a test configuration."""
    return Config.create_test_config()


@pytest.fixture
def sample_stock_data():
    """Create realistic sample stock data for testing."""
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=30),
        end=datetime.now(),
        freq='D'
    )
    
    # Create realistic OHLCV data for AAPL-like stock
    base_price = 150.0
    data = {
        'Open': [base_price + i * 0.5 for i in range(len(dates))],
        'High': [base_price + i * 0.5 + 2 for i in range(len(dates))],
        'Low': [base_price + i * 0.5 - 1.5 for i in range(len(dates))],
        'Close': [base_price + i * 0.5 + 0.5 for i in range(len(dates))],
        'Volume': [1000000 + i * 10000 for i in range(len(dates))]
    }
    
    return pd.DataFrame(data, index=dates)


@pytest.fixture
def dashboard(test_config):
    """Create a StockDashboard instance for testing."""
    return StockDashboard(test_config)


class TestFullAnalysisWorkflow:
    """Test the complete stock analysis workflow."""
    
    def test_full_analysis_with_fresh_data(self, dashboard, sample_stock_data):
        """Test complete analysis workflow when fetching fresh data."""
        
        # Mock only the external API calls
        with patch.object(dashboard.data_provider, 'fetch_stock_data', return_value=sample_stock_data) as mock_fetch, \
             patch.object(dashboard.data_provider, 'validate_symbol', return_value=True) as mock_validate, \
             patch.object(dashboard.ai_generator, 'generate_commentary', return_value="AAPL shows strong upward momentum.") as mock_ai:
            
            # Execute the full workflow
            result = dashboard.get_stock_analysis("AAPL", "1mo", "en")
            
            # Verify external calls were made
            mock_fetch.assert_called_once_with("AAPL", "1mo")
            mock_ai.assert_called_once()
            
            # Verify the result structure
            assert result['symbol'] == 'AAPL'
            assert result['period'] == '1mo'
            assert 'data' in result
            assert 'indicators' in result
            assert 'commentary' in result
            assert 'last_updated' in result
            
            # Verify technical indicators were calculated
            indicators = result['indicators']
            assert 'current_price' in indicators
            assert 'sma_20' in indicators
            assert 'sma_50' in indicators
            assert 'rsi' in indicators
            assert 'trend' in indicators
            assert 'price_change_1d' in indicators
            assert 'price_change_5d' in indicators
            
            # Verify data integrity
            assert len(result['data']) == len(sample_stock_data)
            assert result['commentary'] == "AAPL shows strong upward momentum."
    
    def test_full_analysis_with_cached_data(self, dashboard, sample_stock_data):
        """Test workflow when using cached data."""
        
        with patch.object(dashboard.data_provider, 'fetch_stock_data', return_value=sample_stock_data) as mock_fetch, \
             patch.object(dashboard.ai_generator, 'generate_commentary', return_value="AAPL analysis cached.") as mock_ai:
            
            # First call - should fetch fresh data
            result1 = dashboard.get_stock_analysis("MSFT", "1mo", "en")
            
            # Second call - should use cached data
            result2 = dashboard.get_stock_analysis("MSFT", "1mo", "en")
            
            # Verify fetch was only called once (cached on second call)
            assert mock_fetch.call_count == 1
            
            # Both results should be identical
            assert result1['symbol'] == result2['symbol']
            assert result1['period'] == result2['period']
            assert len(result1['data']) == len(result2['data'])
    
    def test_analysis_with_swedish_language(self, dashboard, sample_stock_data):
        """Test analysis with Swedish language commentary."""
        
        with patch.object(dashboard.data_provider, 'fetch_stock_data', return_value=sample_stock_data), \
             patch.object(dashboard.ai_generator, 'generate_commentary', return_value="TSLA visar stark utveckling.") as mock_ai:
            
            result = dashboard.get_stock_analysis("TSLA", "1mo", "sv")
            
            # Verify Swedish commentary was requested
            args, kwargs = mock_ai.call_args
            assert args[4] == "sv"  # language parameter
            assert result['commentary'] == "TSLA visar stark utveckling."
    
    def test_cache_integration_for_commentary(self, dashboard, sample_stock_data):
        """Test that AI commentary is properly cached."""
        
        with patch.object(dashboard.data_provider, 'fetch_stock_data', return_value=sample_stock_data), \
             patch.object(dashboard.ai_generator, 'generate_commentary', return_value="Cached commentary test.") as mock_ai:
            
            # First analysis
            result1 = dashboard.get_stock_analysis("NVDA", "1mo", "en")
            
            # Second analysis with same parameters (should use cached commentary)
            result2 = dashboard.get_stock_analysis("NVDA", "1mo", "en")
            
            # AI should only be called once due to commentary caching
            assert mock_ai.call_count == 1
            assert result1['commentary'] == result2['commentary']
    
    def test_different_time_periods(self, dashboard, sample_stock_data):
        """Test analysis with different time periods."""
        
        periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y"]
        
        with patch.object(dashboard.data_provider, 'fetch_stock_data', return_value=sample_stock_data), \
             patch.object(dashboard.ai_generator, 'generate_commentary', return_value="Period test commentary."):
            
            for period in periods:
                result = dashboard.get_stock_analysis("GOOGL", period, "en")
                assert result['period'] == period
                assert result['symbol'] == 'GOOGL'
                assert 'indicators' in result
    
    def test_input_validation_integration(self, dashboard):
        """Test that input validation works in the full workflow."""
        
        # Test invalid symbol
        with pytest.raises(ValueError, match="Invalid symbol format"):
            dashboard.get_stock_analysis("invalid@symbol", "1mo", "en")
        
        # Test invalid period
        with pytest.raises(ValueError, match="Invalid period"):
            dashboard.get_stock_analysis("AAPL", "invalid_period", "en")
        
        # Test symbol normalization works
        with patch.object(dashboard.data_provider, 'fetch_stock_data') as mock_fetch, \
             patch.object(dashboard.ai_generator, 'generate_commentary', return_value="Test"):
            
            mock_fetch.return_value = pd.DataFrame({
                'Open': [100], 'High': [105], 'Low': [95], 
                'Close': [102], 'Volume': [1000000]
            }, index=[datetime.now()])
            
            # Lowercase symbol should be normalized to uppercase
            result = dashboard.get_stock_analysis("aapl", "1mo", "en")
            assert result['symbol'] == 'AAPL'
    
    def test_error_handling_integration(self, dashboard):
        """Test error handling in the full workflow."""
        
        # Test data fetching error
        with patch.object(dashboard.data_provider, 'fetch_stock_data', side_effect=Exception("Data fetch failed")):
            
            with pytest.raises(Exception, match="Data fetch failed"):
                dashboard.get_stock_analysis("AAPL", "1mo", "en")
    
    def test_validate_symbol_quick_integration(self, dashboard):
        """Test quick symbol validation."""
        
        # Mock the provider's validate_symbol method
        with patch.object(dashboard.data_provider, 'validate_symbol', return_value=True) as mock_validate:
            result = dashboard.validate_symbol_quick("AAPL")
            assert result is True
            mock_validate.assert_called_once_with("AAPL")
        
        # Test with validation failure
        with patch.object(dashboard.data_provider, 'validate_symbol', side_effect=Exception("Invalid")):
            result = dashboard.validate_symbol_quick("INVALID")
            assert result is False
    
    def test_get_popular_symbols_integration(self, dashboard):
        """Test getting popular symbols."""
        
        symbols = dashboard.get_popular_symbols()
        
        assert isinstance(symbols, list)
        assert len(symbols) > 0
        
        # Verify structure
        for symbol_info in symbols:
            assert 'symbol' in symbol_info
            assert 'name' in symbol_info
            assert isinstance(symbol_info['symbol'], str)
            assert isinstance(symbol_info['name'], str)
        
        # Verify some expected symbols
        symbol_list = [s['symbol'] for s in symbols]
        expected_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
        for expected in expected_symbols:
            assert expected in symbol_list


class TestComponentIntegration:
    """Test that all components work together correctly."""
    
    def test_cache_and_calculator_integration(self, dashboard, sample_stock_data):
        """Test that cache and technical calculator work together."""
        
        with patch.object(dashboard.data_provider, 'fetch_stock_data', return_value=sample_stock_data), \
             patch.object(dashboard.ai_generator, 'generate_commentary', return_value="Integration test."):
            
            # First call
            result1 = dashboard.get_stock_analysis("AMZN", "1mo", "en")
            indicators1 = result1['indicators']
            
            # Second call (should use cached data but recalculate indicators)
            result2 = dashboard.get_stock_analysis("AMZN", "1mo", "en")
            indicators2 = result2['indicators']
            
            # Indicators should be identical (same data, same calculations)
            assert indicators1['current_price'] == indicators2['current_price']
            assert indicators1['sma_20'] == indicators2['sma_20']
            assert indicators1['rsi'] == indicators2['rsi']
            assert indicators1['trend'] == indicators2['trend']
    
    def test_ai_and_cache_integration(self, dashboard, sample_stock_data):
        """Test that AI commentary and cache work together."""
        
        with patch.object(dashboard.data_provider, 'fetch_stock_data', return_value=sample_stock_data), \
             patch.object(dashboard.ai_generator, 'generate_commentary', return_value="AI cache integration.") as mock_ai:
            
            # First call with specific parameters
            result1 = dashboard.get_stock_analysis("META", "1mo", "en")
            
            # Same call should use cached commentary
            result2 = dashboard.get_stock_analysis("META", "1mo", "en")
            
            # Different language should generate new commentary
            result3 = dashboard.get_stock_analysis("META", "1mo", "sv")
            
            # AI should be called twice (once for EN, once for SV)
            assert mock_ai.call_count == 2
            
            # First two should have same commentary (cached)
            assert result1['commentary'] == result2['commentary']
