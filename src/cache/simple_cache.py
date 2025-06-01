import sqlite3
import json
import time
import pandas as pd
from typing import Optional
from pathlib import Path
from io import StringIO


class SimpleCache:
    """Basic SQLite cache for stock data and API responses"""
    
    def __init__(self, db_path: str):
        """Initialize cache with database path
        
        Args:
            db_path: Path to SQLite database file. Use ':memory:' for in-memory testing.
        """
        self.db_path = db_path
        self._connection = None
        
        # For in-memory databases, maintain a persistent connection
        if self.db_path == ':memory:':
            self._connection = sqlite3.connect(self.db_path)
        else:
            self._ensure_db_directory()
        
        self._init_db()
    
    def _ensure_db_directory(self):
        """Create database directory if it doesn't exist"""
        if self.db_path != ':memory:':
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _init_db(self):
        """Initialize database with simple schema"""
        if self._connection:
            # Use persistent connection for in-memory database
            self._connection.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            ''')
            self._connection.commit()
        else:
            # Use context manager for file-based database
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
        """Retrieve cached stock data if fresh
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: Time period (e.g., '1d', '5d', '1mo')
            max_age_hours: Maximum age in hours before data is considered stale
            
        Returns:
            DataFrame with stock data if found and fresh, None otherwise
        """
        key = f"stock_{symbol}_{period}"
        return self._get_dataframe(key, max_age_hours)
    
    def set_stock_data(self, symbol: str, period: str, data: pd.DataFrame):
        """Cache stock data
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: Time period (e.g., '1d', '5d', '1mo')
            data: DataFrame containing stock data to cache
        """
        key = f"stock_{symbol}_{period}"
        self._set_dataframe(key, data)
    
    def get_commentary(self, content_hash: str, max_age_hours: int = 24) -> Optional[str]:
        """Retrieve cached AI commentary
        
        Args:
            content_hash: Hash of the content used to generate commentary
            max_age_hours: Maximum age in hours before commentary is considered stale
            
        Returns:
            Cached commentary text if found and fresh, None otherwise
        """
        key = f"commentary_{content_hash}"
        return self._get_text(key, max_age_hours)
    
    def set_commentary(self, content_hash: str, commentary: str):
        """Cache AI commentary
        
        Args:
            content_hash: Hash of the content used to generate commentary
            commentary: AI generated commentary text to cache
        """
        key = f"commentary_{content_hash}"
        self._set_text(key, commentary)
    
    def _get_dataframe(self, key: str, max_age_hours: int) -> Optional[pd.DataFrame]:
        """Get DataFrame from cache if fresh
        
        Args:
            key: Cache key
            max_age_hours: Maximum age in hours
            
        Returns:
            DataFrame if found and fresh, None otherwise
        """
        data_json = self._get_text(key, max_age_hours)
        if data_json:
            try:
                # Use StringIO and orient='split' to preserve data types and index information
                return pd.read_json(StringIO(data_json), orient='split')
            except (ValueError, TypeError):
                # Remove corrupted data
                self._delete(key)
        return None
    
    def _set_dataframe(self, key: str, data: pd.DataFrame):
        """Store DataFrame as JSON
        
        Args:
            key: Cache key
            data: DataFrame to store
        """
        # Use orient='split' to preserve data types and index information
        self._set_text(key, data.to_json(orient='split'))
    
    def _get_text(self, key: str, max_age_hours: int) -> Optional[str]:
        """Get text data from cache if fresh
        
        Args:
            key: Cache key
            max_age_hours: Maximum age in hours
            
        Returns:
            Cached text if found and fresh, None otherwise
        """
        if self._connection:
            # Use persistent connection for in-memory database
            cursor = self._connection.execute(
                'SELECT data, timestamp FROM cache WHERE key = ?', (key,)
            )
        else:
            # Use context manager for file-based database
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
                        conn.execute('DELETE FROM cache WHERE key = ?', (key,))
                        conn.commit()
                return None
        
        # Handle in-memory database case
        row = cursor.fetchone()
        if row:
            data, timestamp = row
            age_hours = (time.time() - timestamp) / 3600
            if age_hours <= max_age_hours:
                return data
            else:
                # Clean up stale data
                self._connection.execute('DELETE FROM cache WHERE key = ?', (key,))
                self._connection.commit()
        return None

    def _set_text(self, key: str, data: str):
        """Store text data with timestamp
        
        Args:
            key: Cache key
            data: Text data to store
        """
        if self._connection:
            # Use persistent connection for in-memory database
            self._connection.execute(
                'INSERT OR REPLACE INTO cache (key, data, timestamp) VALUES (?, ?, ?)',
                (key, data, time.time())
            )
            self._connection.commit()
        else:
            # Use context manager for file-based database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO cache (key, data, timestamp) VALUES (?, ?, ?)',
                    (key, data, time.time())
                )
                conn.commit()

    def _delete(self, key: str):
        """Delete cache entry
        
        Args:
            key: Cache key to delete
        """
        if self._connection:
            # Use persistent connection for in-memory database
            self._connection.execute('DELETE FROM cache WHERE key = ?', (key,))
            self._connection.commit()
        else:
            # Use context manager for file-based database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM cache WHERE key = ?', (key,))
                conn.commit()
    
    def cleanup_old_data(self, max_age_hours: int = 168) -> int:
        """Remove old cache entries
        
        Args:
            max_age_hours: Maximum age in hours (default: 168 = 1 week)
            
        Returns:
            Number of deleted entries
        """
        cutoff = time.time() - (max_age_hours * 3600)
        
        if self._connection:
            # Use persistent connection for in-memory database
            cursor = self._connection.execute('DELETE FROM cache WHERE timestamp < ?', (cutoff,))
            deleted = cursor.rowcount
            self._connection.commit()
            return deleted
        else:
            # For file-based database, we need to handle the connection directly
            # to get the rowcount before the connection closes
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('DELETE FROM cache WHERE timestamp < ?', (cutoff,))
                deleted = cursor.rowcount
                conn.commit()
                return deleted
    
    def close(self):
        """Close the persistent connection if it exists"""
        if self._connection:
            self._connection.close()
            self._connection = None
