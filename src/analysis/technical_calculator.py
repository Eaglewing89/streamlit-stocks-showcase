"""
Technical Indicator Calculator

This module provides calculations for essential technical indicators used in stock analysis.
It includes methods for calculating Simple Moving Average (SMA), Relative Strength Index (RSI),
price changes, and trend analysis.
"""

import pandas as pd
from typing import Dict, Any, Optional, Union


class TechnicalCalculator:
    """Calculate essential technical indicators for stock analysis"""
    
    @staticmethod
    def calculate_sma(prices: pd.Series, window: int) -> Optional[float]:
        """
        Calculate Simple Moving Average - return latest value
        
        Args:
            prices: Series of stock prices
            window: Number of periods for the moving average
            
        Returns:
            Latest SMA value or None if insufficient data
        """
        if len(prices) < window:
            return None
        return float(prices.rolling(window=window).mean().iloc[-1])
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, window: int = 14) -> Optional[float]:
        """
        Calculate Relative Strength Index - return latest value
        
        Args:
            prices: Series of stock prices
            window: Number of periods for RSI calculation (default 14)
            
        Returns:
            Latest RSI value or None if insufficient data
        """
        if len(prices) < window + 1:
            return None
        
        delta = prices.diff()
        # Calculate gains and losses for RSI using pandas methods
        gains = delta.clip(lower=0.0)  # Keep positive values, set negative to 0
        losses = (-delta).clip(lower=0.0)  # Keep losses as positive values
        
        gain = gains.rolling(window=window).mean()
        loss = losses.rolling(window=window).mean()
        
        # Handle division by zero cases
        latest_gain = gain.iloc[-1]
        latest_loss = loss.iloc[-1]
        
        if latest_loss == 0:
            # No losses: RSI = 100 if there are gains, RSI = 50 if no movement
            rsi_value = 100.0 if latest_gain > 0 else 50.0
        else:
            rs = latest_gain / latest_loss
            rsi_value = 100 - (100 / (1 + rs))
        
        return float(rsi_value)
    
    def calculate_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate all essential indicators
        
        Args:
            data: DataFrame with stock data including 'Close' and 'Volume' columns
            
        Returns:
            Dictionary containing all calculated indicators
            
        Note:
            volume_avg calculates the mean of the last 20 volume entries, or all available
            entries if fewer than 20 records are provided.
        """
        close_prices = data['Close']
        
        indicators = {
            'current_price': float(close_prices.iloc[-1]),
            'sma_20': self.calculate_sma(close_prices, 20),
            'sma_50': self.calculate_sma(close_prices, 50),
            'rsi': self.calculate_rsi(close_prices),
            'volume_avg': float(data['Volume'].tail(20).mean()),
            'price_change_1d': self._calculate_price_change(close_prices, 1),
            'price_change_5d': self._calculate_price_change(close_prices, 5)
        }
        
        # Add trend analysis
        indicators['trend'] = self._analyze_trend(indicators)
        
        return indicators
    
    def _calculate_price_change(self, prices: pd.Series, days: int) -> Dict[str, float]:
        """
        Calculate price change over specified days
        
        Args:
            prices: Series of stock prices
            days: Number of days to look back
            
        Returns:
            Dictionary with 'amount' and 'percent' keys, or default values if insufficient data
        """
        if len(prices) < days + 1:
            return {'amount': 0.0, 'percent': 0.0}
        
        current = float(prices.iloc[-1])
        previous = float(prices.iloc[-(days + 1)])
        amount = current - previous
        percent = (amount / previous) * 100 if previous != 0 else 0.0
        
        return {
            'amount': round(amount, 2),
            'percent': round(percent, 2)
        }
    
    def _analyze_trend(self, indicators: Dict[str, Any]) -> str:
        """
        Simple trend analysis based on moving averages
        
        Args:
            indicators: Dictionary containing calculated indicators
            
        Returns:
            String indicating trend: 'bullish', 'bearish', 'neutral', or 'insufficient_data'
        """
        sma_20 = indicators.get('sma_20')
        sma_50 = indicators.get('sma_50')
        current = indicators.get('current_price')
        
        if not all([sma_20 is not None, sma_50 is not None, current is not None]):
            return 'insufficient_data'
        
        # Safe type assertion after null check - we know these are not None
        sma_20_val = float(sma_20)  # type: ignore
        sma_50_val = float(sma_50)  # type: ignore  
        current_val = float(current)  # type: ignore
        
        if current_val > sma_20_val > sma_50_val:
            return 'bullish'
        elif current_val < sma_20_val < sma_50_val:
            return 'bearish'
        else:
            return 'neutral'
