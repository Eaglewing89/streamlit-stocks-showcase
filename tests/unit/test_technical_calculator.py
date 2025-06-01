"""
Unit tests for TechnicalCalculator

Tests cover SMA, RSI, price change calculations, trend analysis,
and edge cases including insufficient data scenarios.
"""

import pytest
import pandas as pd
import numpy as np
from src.analysis.technical_calculator import TechnicalCalculator


class TestTechnicalCalculator:
    """Test suite for TechnicalCalculator class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.calculator = TechnicalCalculator()
        
        # Create sample data for testing
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        
        # Create realistic price data with trend
        np.random.seed(42)  # For reproducible tests
        base_prices = np.linspace(100, 120, 100)  # Upward trend
        noise = np.random.normal(0, 2, 100)  # Add some volatility
        prices = base_prices + noise
        
        # Ensure prices are positive
        prices = np.maximum(prices, 50)
        
        volumes = np.random.randint(1000000, 5000000, 100)
        
        self.sample_data = pd.DataFrame({
            'Close': prices,
            'Volume': volumes
        }, index=dates)
        
        # Create smaller datasets for edge case testing
        self.small_data_10 = self.sample_data.head(10)
        self.small_data_5 = self.sample_data.head(5)
        self.small_data_1 = self.sample_data.head(1)
    
    def test_sma_calculation_accuracy(self):
        """Test SMA calculation accuracy with known values"""
        # Create simple test data with known SMA
        prices = pd.Series([10, 20, 30, 40, 50])
        
        # Test 3-period SMA
        sma_3 = TechnicalCalculator.calculate_sma(prices, 3)
        expected_sma_3 = (30 + 40 + 50) / 3  # Last 3 values
        assert sma_3 == expected_sma_3
        
        # Test 5-period SMA
        sma_5 = TechnicalCalculator.calculate_sma(prices, 5)
        expected_sma_5 = (10 + 20 + 30 + 40 + 50) / 5  # All values
        assert sma_5 == expected_sma_5
    
    def test_sma_insufficient_data_returns_none(self):
        """Test SMA returns None when insufficient data"""
        prices = pd.Series([10, 20, 30])
        
        # Request 5-period SMA with only 3 data points
        sma = TechnicalCalculator.calculate_sma(prices, 5)
        assert sma is None
        
        # Request 4-period SMA with only 3 data points
        sma = TechnicalCalculator.calculate_sma(prices, 4)
        assert sma is None
        
        # Edge case: exactly the required amount of data
        sma = TechnicalCalculator.calculate_sma(prices, 3)
        assert sma is not None
    
    def test_rsi_calculation_accuracy(self):
        """Test RSI calculation with known values"""
        # Create test data that should produce a specific RSI
        # Using a simple pattern: alternating gains and losses
        prices = pd.Series([100, 102, 100, 103, 99, 105, 98, 107, 96, 110, 
                           94, 112, 92, 115, 90, 118])
        
        rsi = TechnicalCalculator.calculate_rsi(prices, 14)
        
        # RSI should be between 0 and 100
        assert rsi is not None
        assert 0 <= rsi <= 100
        
        # For this alternating pattern, RSI should be around middle range
        assert 30 <= rsi <= 70  # Reasonable range for this pattern
    
    def test_rsi_insufficient_data_returns_none(self):
        """Test RSI returns None when insufficient data"""
        # RSI needs window + 1 data points
        prices = pd.Series([100, 101, 102, 103])  # Only 4 points
        
        # Default RSI (14-period) needs 15 points
        rsi = TechnicalCalculator.calculate_rsi(prices)
        assert rsi is None
        
        # Custom period RSI
        rsi = TechnicalCalculator.calculate_rsi(prices, window=5)
        assert rsi is None  # Still need 6 points for 5-period RSI
        
        # Edge case: exactly the required amount of data
        prices_5 = pd.Series([100, 101, 102, 103, 104])  # 5 points
        rsi = TechnicalCalculator.calculate_rsi(prices_5, window=4)
        assert rsi is not None
    
    def test_price_change_calculation(self):
        """Test price change calculation for different periods"""
        prices = pd.Series([100, 102, 104, 103, 105])
        
        # Test 1-day change
        change_1d = self.calculator._calculate_price_change(prices, 1)
        expected_amount = 105 - 103  # Current vs 1 day ago
        expected_percent = (expected_amount / 103) * 100
        
        assert change_1d['amount'] == round(expected_amount, 2)
        assert change_1d['percent'] == round(expected_percent, 2)
        
        # Test 3-day change
        change_3d = self.calculator._calculate_price_change(prices, 3)
        expected_amount_3d = 105 - 102  # Current vs 3 days ago
        expected_percent_3d = (expected_amount_3d / 102) * 100
        
        assert change_3d['amount'] == round(expected_amount_3d, 2)
        assert change_3d['percent'] == round(expected_percent_3d, 2)
    
    def test_price_change_insufficient_data(self):
        """Test price change with insufficient data"""
        prices = pd.Series([100, 102])  # Only 2 points
        
        # Request 3-day change
        change = self.calculator._calculate_price_change(prices, 3)
        assert change == {'amount': 0, 'percent': 0}
        
        # Request 2-day change (needs 3 points)
        change = self.calculator._calculate_price_change(prices, 2)
        assert change == {'amount': 0, 'percent': 0}
        
        # Edge case: exactly sufficient data
        change = self.calculator._calculate_price_change(prices, 1)
        assert change != {'amount': 0, 'percent': 0}
    
    def test_trend_analysis_bullish(self):
        """Test trend analysis identifies bullish conditions"""
        indicators = {
            'current_price': 110,
            'sma_20': 105,
            'sma_50': 100
        }
        
        trend = self.calculator._analyze_trend(indicators)
        assert trend == 'bullish'
    
    def test_trend_analysis_bearish(self):
        """Test trend analysis identifies bearish conditions"""
        indicators = {
            'current_price': 90,
            'sma_20': 95,
            'sma_50': 100
        }
        
        trend = self.calculator._analyze_trend(indicators)
        assert trend == 'bearish'
    
    def test_trend_analysis_neutral(self):
        """Test trend analysis identifies neutral conditions"""
        # Case 1: Current price between SMAs (bullish condition not met)
        indicators = {
            'current_price': 102,
            'sma_20': 105,
            'sma_50': 100
        }
        trend = self.calculator._analyze_trend(indicators)
        assert trend == 'neutral'
        
        # Case 2: Current above both SMAs but SMAs in wrong order for bullish
        indicators = {
            'current_price': 110,
            'sma_20': 100,
            'sma_50': 105
        }
        trend = self.calculator._analyze_trend(indicators)
        assert trend == 'neutral'
        
        # Case 3: Equal values
        indicators = {
            'current_price': 100,
            'sma_20': 100,
            'sma_50': 100
        }
        trend = self.calculator._analyze_trend(indicators)
        assert trend == 'neutral'
    
    def test_trend_analysis_insufficient_data(self):
        """Test trend analysis with missing indicators"""
        # Missing current_price
        indicators = {
            'sma_20': 105,
            'sma_50': 100
        }
        trend = self.calculator._analyze_trend(indicators)
        assert trend == 'insufficient_data'
        
        # Missing sma_20
        indicators = {
            'current_price': 110,
            'sma_50': 100
        }
        trend = self.calculator._analyze_trend(indicators)
        assert trend == 'insufficient_data'
        
        # Missing sma_50
        indicators = {
            'current_price': 110,
            'sma_20': 105
        }
        trend = self.calculator._analyze_trend(indicators)
        assert trend == 'insufficient_data'
        
        # None values
        indicators = {
            'current_price': 110,
            'sma_20': None,
            'sma_50': 100
        }
        trend = self.calculator._analyze_trend(indicators)
        assert trend == 'insufficient_data'
    
    def test_calculate_indicators_full_workflow(self):
        """Test the main calculate_indicators method"""
        indicators = self.calculator.calculate_indicators(self.sample_data)
        
        # Check all expected keys are present
        expected_keys = [
            'current_price', 'sma_20', 'sma_50', 'rsi', 'volume_avg',
            'price_change_1d', 'price_change_5d', 'trend'
        ]
        
        for key in expected_keys:
            assert key in indicators
        
        # Check types and basic validation
        assert isinstance(indicators['current_price'], (int, float))
        assert indicators['current_price'] > 0
        
        # SMAs should be calculated (we have enough data)
        assert indicators['sma_20'] is not None
        assert indicators['sma_50'] is not None
        assert isinstance(indicators['sma_20'], (int, float))
        assert isinstance(indicators['sma_50'], (int, float))
        
        # RSI should be calculated
        assert indicators['rsi'] is not None
        assert 0 <= indicators['rsi'] <= 100
        
        # Volume average should be positive
        assert indicators['volume_avg'] > 0
        
        # Price changes should be dictionaries
        assert isinstance(indicators['price_change_1d'], dict)
        assert isinstance(indicators['price_change_5d'], dict)
        assert 'amount' in indicators['price_change_1d']
        assert 'percent' in indicators['price_change_1d']
        
        # Trend should be one of the valid values
        assert indicators['trend'] in ['bullish', 'bearish', 'neutral', 'insufficient_data']
    
    def test_calculate_indicators_insufficient_data_scenarios(self):
        """Test calculate_indicators with various insufficient data scenarios"""
        # Test with 10 data points (insufficient for 20-day SMA)
        indicators = self.calculator.calculate_indicators(self.small_data_10)
        
        assert indicators['current_price'] > 0
        assert indicators['sma_20'] is None  # Not enough data
        assert indicators['sma_50'] is None  # Not enough data
        assert indicators['rsi'] is None     # Not enough data (need 15 for default RSI)
        assert indicators['trend'] == 'insufficient_data'  # Missing SMAs
        
        # Price changes should still work with small data
        assert isinstance(indicators['price_change_1d'], dict)
        assert isinstance(indicators['price_change_5d'], dict)
    
    def test_calculate_indicators_minimal_data(self):
        """Test calculate_indicators with minimal data"""
        indicators = self.calculator.calculate_indicators(self.small_data_1)
        
        assert indicators['current_price'] > 0
        assert indicators['sma_20'] is None
        assert indicators['sma_50'] is None
        assert indicators['rsi'] is None
        assert indicators['trend'] == 'insufficient_data'
        
        # Price changes should return defaults with insufficient data
        assert indicators['price_change_1d'] == {'amount': 0, 'percent': 0}
        assert indicators['price_change_5d'] == {'amount': 0, 'percent': 0}
    
    def test_edge_case_zero_prices(self):
        """Test handling of zero/negative prices"""
        # This shouldn't happen in real data, but test robustness
        prices = pd.Series([100, 0, 105])
        
        # Price change calculation should handle zero previous price
        change = self.calculator._calculate_price_change(prices, 1)
        # When previous price is 0, percent should be 0 to avoid division by zero
        assert change['percent'] == 0
        assert change['amount'] == 105  # 105 - 0
    
    def test_static_methods_can_be_called_without_instance(self):
        """Test that static methods work without class instance"""
        prices = pd.Series([100, 102, 104, 106, 108])
        
        # Should work without creating an instance
        sma = TechnicalCalculator.calculate_sma(prices, 3)
        assert sma is not None
        
        rsi = TechnicalCalculator.calculate_rsi(prices, 4)
        assert rsi is not None
        assert 0 <= rsi <= 100


class TestTechnicalCalculatorPerformance:
    """Performance and stress tests for TechnicalCalculator"""
    
    def test_performance_with_large_dataset(self):
        """Test performance with large dataset"""
        calculator = TechnicalCalculator()
        
        # Create large dataset
        dates = pd.date_range('2020-01-01', periods=1000, freq='D')
        prices = np.random.randn(1000).cumsum() + 100
        volumes = np.random.randint(1000000, 10000000, 1000)
        
        large_data = pd.DataFrame({
            'Close': prices,
            'Volume': volumes
        }, index=dates)
        
        # Should complete without errors
        indicators = calculator.calculate_indicators(large_data)
        
        # Basic validation
        assert all(key in indicators for key in [
            'current_price', 'sma_20', 'sma_50', 'rsi', 'volume_avg',
            'price_change_1d', 'price_change_5d', 'trend'
        ])
