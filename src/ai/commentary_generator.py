import hashlib
import json
import time
import pandas as pd
from typing import Dict, Any
from openai import OpenAI


class AICommentaryGenerator:
    """Generate market commentary using OpenAI API"""
    
    def __init__(self, api_key: str):
        """
        Initialize the AI commentary generator.
        
        Args:
            api_key: OpenAI API key for authentication
        """
        self.client = OpenAI(api_key=api_key)
        self.last_call_time = 0
        self.min_interval = 2.0  # 2 seconds between API calls for rate limiting
    
    def generate_commentary(self, symbol: str, data: pd.DataFrame, 
                          indicators: Dict[str, Any], period: str, 
                          language: str = "en") -> str:
        """
        Generate AI commentary with caching and rate limiting.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            data: Stock price data as pandas DataFrame
            indicators: Technical indicators dictionary
            period: Time period for analysis (e.g., '1mo', '3mo')
            language: Language for commentary ('en' or 'sv')
            
        Returns:
            Generated market commentary as string
        """
        try:
            # Simple rate limiting for API calls
            elapsed = time.time() - self.last_call_time
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
            
            self.last_call_time = time.time()
            
            # Build the prompt
            prompt = self._build_prompt(symbol, indicators, period, language)
            
            # Make API call
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            # Handle potential None response content
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("OpenAI API returned empty response")
            
            return content.strip()
            
        except Exception as e:
            # Return fallback commentary on error
            return self._get_fallback_commentary(symbol, indicators, period, language)
    
    def _build_prompt(self, symbol: str, indicators: Dict[str, Any], 
                     period: str, language: str) -> str:
        """
        Build prompt for AI commentary generation.
        
        Args:
            symbol: Stock symbol
            indicators: Technical indicators dictionary
            period: Time period for analysis
            language: Language for commentary
            
        Returns:
            Formatted prompt string for OpenAI API
        """
        lang_instructions = {
            "en": "Generate a professional market commentary in English",
            "sv": "Generera en professionell marknadskommentar på svenska"
        }
        
        instruction = lang_instructions.get(language, lang_instructions["en"])
        
        period_context = {
            "1d": "today's trading",
            "5d": "this week", 
            "1mo": "this month",
            "3mo": "this quarter",
            "6mo": "6 months",
            "1y": "this year"
        }
        
        context = period_context.get(period, f"the {period} period")
        
        prompt = f"""
        {instruction} for stock {symbol} based on {context}:
        
        Current Price: ${indicators.get('current_price', 0):.2f}
        20-day SMA: ${indicators.get('sma_20', 0):.2f}
        50-day SMA: ${indicators.get('sma_50', 0):.2f}
        RSI: {indicators.get('rsi', 0):.1f}
        Trend: {indicators.get('trend', 'neutral')}
        Price Change: {indicators.get('price_change_1d', {}).get('percent', 0):.2f}%
        
        Provide 2-3 sentences focusing on:
        1. Current price movement and trend
        2. Technical indicator signals
        
        Keep it professional and avoid direct investment advice.
        """
        
        return prompt
    
    def _create_content_hash(self, symbol: str, indicators: Dict[str, Any], 
                           period: str, language: str) -> str:
        """
        Create MD5 hash for caching commentary based on key parameters.
        
        Args:
            symbol: Stock symbol
            indicators: Technical indicators dictionary
            period: Time period for analysis
            language: Language for commentary
            
        Returns:
            MD5 hash string for cache key
        """
        # Use key indicator values for hash (rounded for stability)
        key_data = {
            'symbol': symbol,
            'period': period,
            'language': language,
            'current_price': round(indicators.get('current_price', 0), 2),
            'trend': indicators.get('trend', ''),
            'rsi': round(indicators.get('rsi', 0), 0),  # Round RSI to nearest integer
            'price_change': round(indicators.get('price_change_1d', {}).get('percent', 0), 1)
        }
        
        content = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_fallback_commentary(self, symbol: str, indicators: Dict[str, Any], 
                               period: str, language: str) -> str:
        """
        Provide fallback commentary when AI API fails.
        
        Args:
            symbol: Stock symbol
            indicators: Technical indicators dictionary
            period: Time period for analysis
            language: Language for commentary
            
        Returns:
            Template-based fallback commentary
        """
        templates = {
            "en": f"{symbol} is trading at ${indicators.get('current_price', 0):.2f}. "
                  f"Price change: {indicators.get('price_change_1d', {}).get('percent', 0):+.2f}%. "
                  f"Current trend appears {indicators.get('trend', 'neutral')}.",
            
            "sv": f"{symbol} handlas för ${indicators.get('current_price', 0):.2f}. "
                  f"Prisförändring: {indicators.get('price_change_1d', {}).get('percent', 0):+.2f}%. "
                  f"Nuvarande trend verkar {indicators.get('trend', 'neutral')}."
        }
        
        return templates.get(language, templates["en"])
