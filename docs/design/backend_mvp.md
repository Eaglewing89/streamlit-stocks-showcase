# Backend MVP Architecture

**Simple, Solid Foundation for Stock Dashboard**

## Overview

This MVP backend architecture focuses on core functionality with minimal complexity while maintaining clean software engineering practices. It provides a foundation that can be expanded upon without significant refactoring.

## Core Principles

- **Simplicity First**: No premature optimization or enterprise patterns
- **Clean Architecture**: Clear separation of concerns without over-engineering
- **Extensible Design**: Easy to add features without major refactoring
- **Fast Implementation**: Can be built and tested quickly

## Architecture

### Simplified Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 StockDashboard                              │
│  - Main coordinator class                                   │
│  - Simple error handling                                    │
│  - Basic logging                                            │
└─────┬─────────┬──────────────┬─────────────────────────────┘
      │         │              │
┌──── ▼ ───┐ ┌─ ▼ ──────┐ ┌─── ▼ ────┐
│   Data   │ │Technical │ │   AI     │
│ Provider │ │Calculator│ │Generator │
│          │ │          │ │          │
└──────────┘ └──────────┘ └──────────┘
      │                        │
┌──── ▼ ────────────────────── ▼ ──┐
│         Simple Cache             │
│      (SQLite + JSON)             │
└──────────────────────────────────┘
```

### Component Responsibilities

- **`StockDashboard`**: Main orchestrator - coordinates all operations
- **`YFinanceProvider`**: Fetches stock data from Yahoo Finance
- **`TechnicalCalculator`**: Computes essential technical indicators  
- **`AICommentaryGenerator`**: Generates market commentary using OpenAI
- **`SimpleCache`**: Basic SQLite caching for data and API responses
- **`Config`**: Simple configuration management

## Project Structure

```
stock-dashboard/
├── src/                            # Source code
│   ├── __init__.py
│   ├── config.py                   # Configuration management
│   ├── dashboard.py                # Main StockDashboard orchestrator
│   ├── cache/
│   │   ├── __init__.py
│   │   └── simple_cache.py         # SQLite caching implementation
│   ├── data/
│   │   ├── __init__.py
│   │   └── yfinance_provider.py    # Yahoo Finance data provider
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── technical_calculator.py # Technical indicators
│   └── ai/
│       ├── __init__.py
│       └── commentary_generator.py # OpenAI commentary generation
├── tests/                          # Test suite (as defined in testing_mvp.md)
│   ├── unit/
│   ├── integration/
│   ├── fixtures/
│   └── factories/
├── data/                           # Data storage
│   ├── cache.db                    # SQLite cache database
│   └── logs/                       # Application logs
├── streamlit/                      # Frontend application (as defined in frontend_mvp.md)
│   ├── app.py
│   ├── components/
│   ├── utils/
│   └── config/
├── docs/                           # Documentation
│   └── design/                     # Design documents
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
└── README.md                       # Project documentation
```

## File Mapping to Components

### Core Backend Files

| Component | File Path | Purpose |
|-----------|-----------|---------|
| **Config** | `src/config.py` | Environment variables, validation, test config factory |
| **SimpleCache** | `src/cache/simple_cache.py` | SQLite operations, data serialization, TTL management |
| **YFinanceProvider** | `src/data/yfinance_provider.py` | Stock data fetching, rate limiting, symbol validation |
| **TechnicalCalculator** | `src/analysis/technical_calculator.py` | SMA, RSI, trend analysis, price change calculations |
| **AICommentaryGenerator** | `src/ai/commentary_generator.py` | OpenAI API calls, prompt building, fallback commentary |
| **StockDashboard** | `src/dashboard.py` | Main orchestrator, workflow coordination, error handling |

### Supporting Files

| Type | File Path | Purpose |
|------|-----------|---------|
| **Main App** | `streamlit/app.py` | Streamlit application entry point |
| **Dependencies** | `requirements.txt` | Python package requirements |
| **Environment** | `.env.example` | Template for environment variables |
| **Database** | `data/cache.db` | SQLite cache storage |
| **Tests** | `tests/unit/test_*.py` | Component unit tests |
| **Integration** | `tests/integration/test_*.py` | End-to-end workflow tests |
```python

## Implementation

### 1. Configuration

```python
import os
from typing import Optional

class Config:
    """Simple configuration management"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.db_path = os.getenv('DB_PATH', 'data/cache.db')
        self.cache_hours = int(os.getenv('CACHE_HOURS', '1'))
        
        # Validate required settings
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    @classmethod
    def create_test_config(cls, openai_key: str = "test_key") -> 'Config':
        """Create configuration for testing"""
        config = cls.__new__(cls)
        config.openai_api_key = openai_key
        config.db_path = ':memory:'  # In-memory SQLite for tests
        config.cache_hours = 1
        return config
```

### 2. Simple Cache

```python
import sqlite3
import json
import time
import pandas as pd
from typing import Optional
from pathlib import Path

class SimpleCache:
    """Basic SQLite cache for stock data and API responses"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_db()
    
    def _ensure_db_directory(self):
        """Create database directory if it doesn't exist"""
        if self.db_path != ':memory:':
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _init_db(self):
        """Initialize database with simple schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            ''')
            conn.commit()
    
    def get_stock_data(self, symbol: str, period: str, max_age_hours: int = 1) -> Optional[pd.DataFrame]:
        """Retrieve cached stock data if fresh"""
        key = f"stock_{symbol}_{period}"
        return self._get_dataframe(key, max_age_hours)
    
    def set_stock_data(self, symbol: str, period: str, data: pd.DataFrame):
        """Cache stock data"""
        key = f"stock_{symbol}_{period}"
        self._set_dataframe(key, data)
    
    def get_commentary(self, content_hash: str, max_age_hours: int = 24) -> Optional[str]:
        """Retrieve cached AI commentary"""
        key = f"commentary_{content_hash}"
        return self._get_text(key, max_age_hours)
    
    def set_commentary(self, content_hash: str, commentary: str):
        """Cache AI commentary"""
        key = f"commentary_{content_hash}"
        self._set_text(key, commentary)
    
    def _get_dataframe(self, key: str, max_age_hours: int) -> Optional[pd.DataFrame]:
        """Get DataFrame from cache if fresh"""
        data_json = self._get_text(key, max_age_hours)
        if data_json:
            try:
                return pd.read_json(data_json)
            except (ValueError, TypeError):
                # Remove corrupted data
                self._delete(key)
        return None
    
    def _set_dataframe(self, key: str, data: pd.DataFrame):
        """Store DataFrame as JSON"""
        self._set_text(key, data.to_json())
    
    def _get_text(self, key: str, max_age_hours: int) -> Optional[str]:
        """Get text data from cache if fresh"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT data, timestamp FROM cache WHERE key = ?', (key,)
            )
            row = cursor.fetchone()
            
            if row:
                data, timestamp = row
                age_hours = (time.time() - timestamp) / 3600
                if age_hours <= max_age_hours:
                    return data
                else:
                    # Clean up stale data
                    self._delete(key)
        return None
    
    def _set_text(self, key: str, data: str):
        """Store text data with timestamp"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'INSERT OR REPLACE INTO cache (key, data, timestamp) VALUES (?, ?, ?)',
                (key, data, time.time())
            )
            conn.commit()
    
    def _delete(self, key: str):
        """Delete cache entry"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM cache WHERE key = ?', (key,))
            conn.commit()
    
    def cleanup_old_data(self, max_age_hours: int = 168):  # 1 week default
        """Remove old cache entries"""
        cutoff = time.time() - (max_age_hours * 3600)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('DELETE FROM cache WHERE timestamp < ?', (cutoff,))
            deleted = cursor.rowcount
            conn.commit()
        return deleted
```

### 3. Data Provider

```python
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

class YFinanceProvider:
    """Simple Yahoo Finance data provider with basic rate limiting"""
    
    def __init__(self):
        self.last_call_time = 0
        self.min_interval = 1.0  # 1 second between calls
    
    def fetch_stock_data(self, symbol: str, period: str) -> pd.DataFrame:
        """Fetch stock data with simple rate limiting"""
        # Simple rate limiting
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        self.last_call_time = time.time()
        
        # Fetch data
        symbol = symbol.upper().strip()
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        if data.empty:
            raise ValueError(f"No data found for symbol: {symbol}")
        
        # Basic data validation
        if len(data) < 5:  # Need minimum data for indicators
            raise ValueError(f"Insufficient data for {symbol}")
        
        return data
    
    def validate_symbol(self, symbol: str) -> bool:
        """Quick symbol validation"""
        try:
            symbol = symbol.upper().strip()
            if not symbol or len(symbol) > 5:
                return False
            
            # Try to fetch just one day of data for validation
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            return not data.empty
        except:
            return False
```

### 4. Technical Calculator

```python
import pandas as pd
from typing import Dict, Any

class TechnicalCalculator:
    """Calculate essential technical indicators"""
    
    @staticmethod
    def calculate_sma(prices: pd.Series, window: int) -> float:
        """Calculate Simple Moving Average - return latest value"""
        if len(prices) < window:
            return None
        return prices.rolling(window=window).mean().iloc[-1]
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, window: int = 14) -> float:
        """Calculate RSI - return latest value"""
        if len(prices) < window + 1:
            return None
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def calculate_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all essential indicators"""
        close_prices = data['Close']
        
        indicators = {
            'current_price': close_prices.iloc[-1],
            'sma_20': self.calculate_sma(close_prices, 20),
            'sma_50': self.calculate_sma(close_prices, 50),
            'rsi': self.calculate_rsi(close_prices),
            'volume_avg': data['Volume'].tail(20).mean(),
            'price_change_1d': self._calculate_price_change(close_prices, 1),
            'price_change_5d': self._calculate_price_change(close_prices, 5)
        }
        
        # Add trend analysis
        indicators['trend'] = self._analyze_trend(indicators)
        
        return indicators
    
    def _calculate_price_change(self, prices: pd.Series, days: int) -> Dict[str, float]:
        """Calculate price change over specified days"""
        if len(prices) < days + 1:
            return {'amount': 0, 'percent': 0}
        
        current = prices.iloc[-1]
        previous = prices.iloc[-(days + 1)]
        amount = current - previous
        percent = (amount / previous) * 100 if previous != 0 else 0
        
        return {
            'amount': round(amount, 2),
            'percent': round(percent, 2)
        }
    
    def _analyze_trend(self, indicators: Dict[str, Any]) -> str:
        """Simple trend analysis based on moving averages"""
        sma_20 = indicators.get('sma_20')
        sma_50 = indicators.get('sma_50')
        current = indicators.get('current_price')
        
        if not all([sma_20, sma_50, current]):
            return 'insufficient_data'
        
        if current > sma_20 > sma_50:
            return 'bullish'
        elif current < sma_20 < sma_50:
            return 'bearish'
        else:
            return 'neutral'
```

### 5. AI Commentary Generator

```python
import hashlib
from openai import OpenAI
from typing import Dict, Any

class AICommentaryGenerator:
    """Generate market commentary using OpenAI API"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.last_call_time = 0
        self.min_interval = 2.0  # 2 seconds between API calls
    
    def generate_commentary(self, symbol: str, data: pd.DataFrame, 
                          indicators: Dict[str, Any], period: str, 
                          language: str = "en") -> str:
        """Generate AI commentary with caching"""
        try:
            # Create content hash for caching
            content_hash = self._create_content_hash(symbol, indicators, period, language)
            
            # Simple rate limiting for API calls
            elapsed = time.time() - self.last_call_time
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
            
            self.last_call_time = time.time()
            
            prompt = self._build_prompt(symbol, indicators, period, language)
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Return fallback commentary on error
            return self._get_fallback_commentary(symbol, indicators, period, language)
    
    def _build_prompt(self, symbol: str, indicators: Dict[str, Any], 
                     period: str, language: str) -> str:
        """Build prompt for AI commentary"""
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
        """Create hash for caching commentary"""
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
        """Provide fallback commentary when AI fails"""
        templates = {
            "en": f"{symbol} is trading at ${indicators.get('current_price', 0):.2f}. "
                  f"Price change: {indicators.get('price_change_1d', {}).get('percent', 0):+.2f}%. "
                  f"Current trend appears {indicators.get('trend', 'neutral')}.",
            
            "sv": f"{symbol} handlas för ${indicators.get('current_price', 0):.2f}. "
                  f"Prisförändring: {indicators.get('price_change_1d', {}).get('percent', 0):+.2f}%. "
                  f"Nuvarande trend verkar {indicators.get('trend', 'neutral')}."
        }
        
        return templates.get(language, templates["en"])
```

### 6. Main Orchestrator

```python
import logging
from typing import Dict, Any, List

class StockDashboard:
    """Main coordinator for stock dashboard operations"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.cache = SimpleCache(self.config.db_path)
        self.data_provider = YFinanceProvider()
        self.calculator = TechnicalCalculator()
        self.ai_generator = AICommentaryGenerator(self.config.openai_api_key)
        
        # Simple logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_stock_analysis(self, symbol: str, period: str = "1mo", 
                          language: str = "en") -> Dict[str, Any]:
        """Main entry point for stock analysis"""
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
                    symbol, data, indicators, period, language
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
        """Quick symbol validation for UI"""
        try:
            return self.data_provider.validate_symbol(symbol)
        except:
            return False
    
    def get_popular_symbols(self) -> List[Dict[str, str]]:
        """Get list of popular symbols for UI"""
        return [
            {'symbol': 'AAPL', 'name': 'Apple Inc.'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corp.'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corp.'},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.'}
        ]
    
    def cleanup_cache(self, max_age_hours: int = 168) -> int:
        """Clean up old cache entries"""
        return self.cache.cleanup_old_data(max_age_hours)
    
    def _validate_symbol(self, symbol: str) -> str:
        """Basic symbol validation"""
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Symbol must be a non-empty string")
        
        symbol = symbol.upper().strip()
        if len(symbol) > 5 or not symbol.isalpha():
            raise ValueError(f"Invalid symbol format: {symbol}")
        
        return symbol
    
    def _validate_period(self, period: str) -> str:
        """Basic period validation"""
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y']
        if period not in valid_periods:
            raise ValueError(f"Invalid period: {period}. Must be one of {valid_periods}")
        return period
```

## Usage Example

```python
# Basic usage - using organized imports
from src.dashboard import StockDashboard
from src.config import Config

# Initialize with default config
dashboard = StockDashboard()

# Or with custom config
config = Config()
dashboard = StockDashboard(config)

# Get analysis
result = dashboard.get_stock_analysis('AAPL', '1mo')

print(f"Symbol: {result['symbol']}")
print(f"Current Price: ${result['indicators']['current_price']:.2f}")
print(f"Trend: {result['indicators']['trend']}")
print(f"Commentary: {result['commentary']}")
```

## Import Structure

With the organized file structure, imports will be clean and logical:

```python
# Main orchestrator
from src.dashboard import StockDashboard

# Configuration
from src.config import Config

# Individual components (for testing or custom usage)
from src.cache.simple_cache import SimpleCache
from src.data.yfinance_provider import YFinanceProvider
from src.analysis.technical_calculator import TechnicalCalculator
from src.ai.commentary_generator import AICommentaryGenerator

# Streamlit app components
from streamlit.components.charts import create_price_chart
from streamlit.components.sidebar import create_sidebar_controls
from streamlit.components.display import display_analysis_results
```

## Development Workflow

### 1. Initial Setup
```bash
# Create project structure
mkdir -p src/{cache,data,analysis,ai}
mkdir -p streamlit/{components,utils}
mkdir -p tests/{unit,integration,fixtures,factories}
mkdir -p data/logs
touch src/__init__.py src/cache/__init__.py src/data/__init__.py
touch src/analysis/__init__.py src/ai/__init__.py
touch streamlit/components/__init__.py streamlit/utils/__init__.py
```

### 2. Implementation Order
1. **src/config.py** - Configuration foundation
2. **src/cache/simple_cache.py** - Data persistence
3. **src/analysis/technical_calculator.py** - Pure calculation logic
4. **src/data/yfinance_provider.py** - External data fetching
5. **src/ai/commentary_generator.py** - AI integration
6. **src/dashboard.py** - Main orchestrator
7. **streamlit/app.py** - Frontend application

### 3. Testing Integration
- Unit tests mirror the src/ structure in tests/unit/
- Each component can be tested independently
- Integration tests validate the complete workflow

## File Size Guidelines

To maintain simplicity and readability:

| File | Target Lines | Purpose |
|------|-------------|---------|
| `config.py` | ~50 lines | Simple configuration with validation |
| `simple_cache.py` | ~150 lines | SQLite operations and serialization |
| `yfinance_provider.py` | ~100 lines | Data fetching with rate limiting |
| `technical_calculator.py` | ~120 lines | Indicator calculations |
| `commentary_generator.py` | ~150 lines | AI integration with fallbacks |
| `dashboard.py` | ~200 lines | Main orchestration logic |
| `app.py` | ~200 lines | Streamlit UI and user interactions |

## Dependencies

```
# Core backend
yfinance>=0.2.18
pandas>=2.0.0
openai>=1.0.0


# Frontend
streamlit>=1.28.0
plotly>=5.15.0

# Development & Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
requests-mock>=1.11.0
```


## Future Expansion Paths

This MVP architecture provides clear extension points for future enhancements:

### **Easy Additions:**
- **More Indicators**: Add methods to `TechnicalCalculator`
- **Better Caching**: Enhance `SimpleCache` with TTL management
- **Input Validation**: Add validation decorator to methods
- **Error Types**: Create specific exception classes

### **Medium Additions:**
- **Rate Limiting**: Add decorator pattern for API calls
- **Configuration**: Expand `Config` with validation
- **Logging**: Enhanced logging with different levels
- **Data Sources**: Create provider interface for multiple data sources

### **Advanced Additions:**
- **Async Operations**: Convert to async/await pattern
- **Background Jobs**: Add task queue for data refresh
- **Database Optimization**: Add indexes and query optimization
- **Monitoring**: Add health checks and metrics

## Key Benefits

1. **Fast Implementation**: Can be built in 1-2 days
2. **Easy Testing**: Simple components with clear interfaces
3. **Clear Structure**: Easy to understand and modify
4. **Extensible**: Natural paths for adding complexity
5. **Reliable**: Fewer moving parts = fewer failure points

This MVP focuses on delivering core value quickly while maintaining a clean foundation for future growth.
