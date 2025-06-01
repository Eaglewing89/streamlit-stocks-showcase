"""
Main orchestrator for stock dashboard operations.

This module contains the StockDashboard class which coordinates
all backend operations including data fetching, technical analysis,
AI commentary generation, and caching.
"""

import logging
import re
from typing import Dict, Any, List, Optional

from .config import Config
from .cache.simple_cache import SimpleCache
from .data.yfinance_provider import YFinanceProvider
from .analysis.technical_calculator import TechnicalCalculator
from .ai.commentary_generator import AICommentaryGenerator


class StockDashboard:
    """Main coordinator for stock dashboard operations"""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the stock dashboard with all required components"""
        self.config = config or Config()
        self.cache = SimpleCache(self.config.db_path)
        self.data_provider = YFinanceProvider()
        self.calculator = TechnicalCalculator()
        
        # Ensure we have a valid API key
        if not self.config.openai_api_key:
            raise ValueError("OpenAI API key is required")
        self.ai_generator = AICommentaryGenerator(self.config.openai_api_key)
        
        # Get logger (without configuring global settings)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("StockDashboard initialized successfully")
    
    def get_stock_analysis(self, symbol: str, period: str = "1mo", 
                          language: str = "en") -> Dict[str, Any]:
        """
        Main entry point for stock analysis.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: Time period for analysis ('1d', '5d', '1mo', '3mo', '6mo', '1y')
            language: Language for commentary ('en', 'sv')
            
        Returns:
            Dictionary containing symbol, period, data, indicators, commentary, and last_updated
            
        Raises:
            ValueError: If symbol or period is invalid
            Exception: If data fetching or analysis fails
        """
        try:
            # Input validation
            symbol = self._validate_symbol(symbol)
            period = self._validate_period(period)
            
            self.logger.info(f"Analyzing {symbol} for {period}")
            
            # Try to get cached data
            data = self.cache.get_stock_data(symbol, period, self.config.cache_hours)
            
            # Fetch fresh data if needed
            if data is None:
                self.logger.info(f"Fetching fresh data for {symbol}")
                data = self.data_provider.fetch_stock_data(symbol, period)
                self.cache.set_stock_data(symbol, period, data)
            else:
                self.logger.info(f"Using cached data for {symbol}")
            
            # Calculate indicators
            indicators = self.calculator.calculate_indicators(data)
            
            # Generate AI commentary (with caching)
            content_hash = self.ai_generator._create_content_hash(
                symbol, indicators, period, language
            )
            commentary = self.cache.get_commentary(content_hash, max_age_hours=24)
            
            if commentary is None:
                self.logger.info("Generating fresh AI commentary")
                commentary = self.ai_generator.generate_commentary(
                    symbol, indicators, period, language
                )
                self.cache.set_commentary(content_hash, commentary)
            else:
                self.logger.info("Using cached AI commentary")
            
            return {
                'symbol': symbol,
                'period': period,
                'data': data,
                'indicators': indicators,
                'commentary': commentary,
                'last_updated': data.index[-1].strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {str(e)}")
            raise
    
    def validate_symbol_quick(self, symbol: str) -> bool:
        """
        Quick symbol validation for UI.
        
        Args:
            symbol: Stock symbol to validate
            
        Returns:
            True if symbol is valid, False otherwise
        """
        try:
            return self.data_provider.validate_symbol(symbol)
        except Exception:
            return False
    
    def get_popular_symbols(self) -> List[Dict[str, str]]:
        """
        Get list of popular symbols for UI.
        
        Returns:
            List of dictionaries with 'symbol' and 'name' keys
        """
        return [
            {'symbol': 'AAPL', 'name': 'Apple Inc.'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corp.'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corp.'},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.'}
        ]
    
    def _validate_symbol(self, symbol: str) -> str:
        """
        Validate and normalize stock symbol.
        
        Args:
            symbol: Raw symbol input
            
        Returns:
            Normalized symbol (uppercase, alphanumeric)
            
        Raises:
            ValueError: If symbol is invalid
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Symbol must be a non-empty string")
        
        # Clean and normalize
        symbol = symbol.strip().upper()
        
        # Basic validation - alphanumeric, dots allowed for some symbols
        if not re.match(r'^[A-Z0-9\.-]+$', symbol):
            raise ValueError(f"Invalid symbol format: {symbol}")
        
        # Length check
        if len(symbol) < 1 or len(symbol) > 10:
            raise ValueError(f"Symbol length must be 1-10 characters: {symbol}")
        
        return symbol
    
    def _validate_period(self, period: str) -> str:
        """
        Validate time period for analysis.
        
        Args:
            period: Raw period input
            
        Returns:
            Validated period
            
        Raises:
            ValueError: If period is invalid
        """
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        
        if not period or not isinstance(period, str):
            raise ValueError("Period must be a non-empty string")
        
        period = period.lower().strip()
        
        if period not in valid_periods:
            raise ValueError(f"Invalid period: {period}. Valid periods: {valid_periods}")
        
        return period
