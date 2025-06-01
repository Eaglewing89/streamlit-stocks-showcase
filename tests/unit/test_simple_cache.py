import pytest
import pandas as pd
import time
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch

from src.cache.simple_cache import SimpleCache
from src.config import Config


class TestSimpleCache:
    """Test suite for the SimpleCache class"""
    
    @pytest.fixture
    def test_cache(self):
        """Create cache instance with in-memory database for testing"""
        # Each test gets a fresh cache instance with its own in-memory database
        cache = SimpleCache(':memory:')
        return cache
    
    @pytest.fixture
    def sample_stock_data(self):
        """Create sample stock data DataFrame for testing"""
        data = {
            'Open': [100.0, 101.0, 102.0],
            'High': [105.0, 106.0, 107.0],
            'Low': [99.0, 100.0, 101.0],
            'Close': [104.0, 105.0, 106.0],
            'Volume': [1000000, 1100000, 1200000]
        }
        return pd.DataFrame(data, index=pd.date_range('2023-01-01', periods=3))
    
    def test_cache_initialization_in_memory(self):
        """Test cache initialization with in-memory database"""
        cache = SimpleCache(':memory:')
        assert cache.db_path == ':memory:'
        assert cache._connection is not None
        
        # Verify table was created by trying to query it using the persistent connection
        cursor = cache._connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cache'")
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == 'cache'
        
        # Clean up
        cache.close()
    
    def test_cache_initialization_with_file_path(self):
        """Test cache initialization with file database and directory creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / 'test_cache' / 'cache.db'
            cache = SimpleCache(str(db_path))
            
            # Verify directory was created
            assert db_path.parent.exists()
            
            # Verify database file was created
            assert db_path.exists()
            
            # Verify table was created
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cache'")
                assert cursor.fetchone() is not None
    
    def test_stock_data_storage_and_retrieval(self, test_cache, sample_stock_data):
        """Test storing and retrieving stock data"""
        symbol = 'AAPL'
        period = '1d'
        
        # Store data
        test_cache.set_stock_data(symbol, period, sample_stock_data)
        
        # Retrieve data
        retrieved_data = test_cache.get_stock_data(symbol, period, max_age_hours=1)
        
        # Verify data is identical
        assert retrieved_data is not None
        
        # Check that the data values are the same (ignore dtype and freq differences from JSON serialization)
        pd.testing.assert_frame_equal(retrieved_data, sample_stock_data, check_freq=False, check_dtype=False)
        
        # Verify the shape and columns are preserved
        assert retrieved_data.shape == sample_stock_data.shape
        assert list(retrieved_data.columns) == list(sample_stock_data.columns)
        assert list(retrieved_data.index) == list(sample_stock_data.index)
    
    def test_stock_data_expiration(self, test_cache, sample_stock_data):
        """Test that expired stock data is not retrieved and is deleted"""
        symbol = 'AAPL'
        period = '1d'
        
        # Store data
        test_cache.set_stock_data(symbol, period, sample_stock_data)
        
        # Mock time to make data appear old
        with patch('time.time', return_value=time.time() + 3600 * 2):  # 2 hours later
            # Try to retrieve with 1 hour max age
            retrieved_data = test_cache.get_stock_data(symbol, period, max_age_hours=1)
            assert retrieved_data is None
        
        # Verify the expired data was deleted
        retrieved_data = test_cache.get_stock_data(symbol, period, max_age_hours=24)
        assert retrieved_data is None
    
    def test_stock_data_fresh_within_max_age(self, test_cache, sample_stock_data):
        """Test that fresh data is retrieved when within max_age_hours"""
        symbol = 'AAPL'
        period = '1d'
        
        # Store data
        test_cache.set_stock_data(symbol, period, sample_stock_data)
        
        # Mock time to make data appear slightly old but within limit
        with patch('time.time', return_value=time.time() + 1800):  # 30 minutes later
            retrieved_data = test_cache.get_stock_data(symbol, period, max_age_hours=1)
            assert retrieved_data is not None
            pd.testing.assert_frame_equal(retrieved_data, sample_stock_data, check_freq=False, check_dtype=False)
    
    def test_commentary_storage_and_retrieval(self, test_cache):
        """Test storing and retrieving AI commentary"""
        content_hash = 'test_hash_123'
        commentary = 'AAPL is showing strong bullish momentum with RSI at 65.'
        
        # Store commentary
        test_cache.set_commentary(content_hash, commentary)
        
        # Retrieve commentary
        retrieved_commentary = test_cache.get_commentary(content_hash, max_age_hours=24)
        
        assert retrieved_commentary == commentary
    
    def test_commentary_expiration(self, test_cache):
        """Test that expired commentary is not retrieved and is deleted"""
        content_hash = 'test_hash_123'
        commentary = 'AAPL is showing strong bullish momentum.'
        
        # Store commentary
        test_cache.set_commentary(content_hash, commentary)
        
        # Mock time to make commentary appear old
        with patch('time.time', return_value=time.time() + 3600 * 25):  # 25 hours later
            # Try to retrieve with 24 hour max age
            retrieved_commentary = test_cache.get_commentary(content_hash, max_age_hours=24)
            assert retrieved_commentary is None
        
        # Verify the expired commentary was deleted
        retrieved_commentary = test_cache.get_commentary(content_hash, max_age_hours=48)
        assert retrieved_commentary is None
    
    def test_corrupted_dataframe_handling(self, test_cache):
        """Test handling of corrupted DataFrame data in cache"""
        key = 'stock_AAPL_1d'
        
        # Manually insert corrupted JSON data
        if test_cache._connection:
            # Use persistent connection for in-memory database
            test_cache._connection.execute(
                'INSERT INTO cache (key, data, timestamp) VALUES (?, ?, ?)',
                (key, 'invalid_json_data', time.time())
            )
            test_cache._connection.commit()
        else:
            # Use context manager for file-based database
            with sqlite3.connect(test_cache.db_path) as conn:
                conn.execute(
                    'INSERT INTO cache (key, data, timestamp) VALUES (?, ?, ?)',
                    (key, 'invalid_json_data', time.time())
                )
                conn.commit()
        
        # Try to retrieve - should return None and delete corrupted entry
        retrieved_data = test_cache.get_stock_data('AAPL', '1d', max_age_hours=1)
        assert retrieved_data is None
        
        # Verify corrupted data was deleted
        if test_cache._connection:
            cursor = test_cache._connection.execute('SELECT data FROM cache WHERE key = ?', (key,))
            assert cursor.fetchone() is None
        else:
            with sqlite3.connect(test_cache.db_path) as conn:
                cursor = conn.execute('SELECT data FROM cache WHERE key = ?', (key,))
                assert cursor.fetchone() is None
    
    def test_cleanup_old_data(self, test_cache, sample_stock_data):
        """Test cleanup of old cache entries"""
        # Insert some test data with different timestamps
        current_time = time.time()
        
        # Fresh data (1 hour old)
        fresh_key = 'stock_AAPL_1d'
        if test_cache._connection:
            test_cache._connection.execute(
                'INSERT INTO cache (key, data, timestamp) VALUES (?, ?, ?)',
                (fresh_key, sample_stock_data.to_json(), current_time - 3600)
            )
        else:
            with sqlite3.connect(test_cache.db_path) as conn:
                conn.execute(
                    'INSERT INTO cache (key, data, timestamp) VALUES (?, ?, ?)',
                    (fresh_key, sample_stock_data.to_json(), current_time - 3600)
                )
        
        # Old data (1 week + 1 hour old)
        old_key = 'stock_MSFT_1d'
        if test_cache._connection:
            test_cache._connection.execute(
                'INSERT INTO cache (key, data, timestamp) VALUES (?, ?, ?)',
                (old_key, sample_stock_data.to_json(), current_time - (168 * 3600 + 3600))
            )
            test_cache._connection.commit()
        else:
            with sqlite3.connect(test_cache.db_path) as conn:
                conn.execute(
                    'INSERT INTO cache (key, data, timestamp) VALUES (?, ?, ?)',
                    (old_key, sample_stock_data.to_json(), current_time - (168 * 3600 + 3600))
                )
                conn.commit()
        
        # Clean up data older than 1 week (168 hours)
        deleted_count = test_cache.cleanup_old_data(max_age_hours=168)
        assert deleted_count == 1
        
        # Verify fresh data still exists
        if test_cache._connection:
            cursor = test_cache._connection.execute('SELECT data FROM cache WHERE key = ?', (fresh_key,))
            assert cursor.fetchone() is not None
        else:
            with sqlite3.connect(test_cache.db_path) as conn:
                cursor = conn.execute('SELECT data FROM cache WHERE key = ?', (fresh_key,))
                assert cursor.fetchone() is not None
        
        # Verify old data was deleted
        if test_cache._connection:
            cursor = test_cache._connection.execute('SELECT data FROM cache WHERE key = ?', (old_key,))
            assert cursor.fetchone() is None
        else:
            with sqlite3.connect(test_cache.db_path) as conn:
                cursor = conn.execute('SELECT data FROM cache WHERE key = ?', (old_key,))
                assert cursor.fetchone() is None
    
    def test_different_symbols_and_periods_are_cached_separately(self, test_cache, sample_stock_data):
        """Test that different symbols and periods are cached independently"""
        # Store data for different symbols and periods
        test_cache.set_stock_data('AAPL', '1d', sample_stock_data)
        test_cache.set_stock_data('MSFT', '1d', sample_stock_data)
        test_cache.set_stock_data('AAPL', '5d', sample_stock_data)
        
        # Verify all are retrievable independently
        aapl_1d = test_cache.get_stock_data('AAPL', '1d', max_age_hours=1)
        msft_1d = test_cache.get_stock_data('MSFT', '1d', max_age_hours=1)
        aapl_5d = test_cache.get_stock_data('AAPL', '5d', max_age_hours=1)
        
        assert aapl_1d is not None
        assert msft_1d is not None
        assert aapl_5d is not None
        
        # Verify they are separate entries by checking the cache directly
        if test_cache._connection:
            cursor = test_cache._connection.execute('SELECT COUNT(*) FROM cache')
            count = cursor.fetchone()[0]
            assert count == 3
        else:
            with sqlite3.connect(test_cache.db_path) as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM cache')
                count = cursor.fetchone()[0]
                assert count == 3
    
    def test_commentary_different_hashes_cached_separately(self, test_cache):
        """Test that commentary with different content hashes are cached separately"""
        hash1 = 'hash_123'
        hash2 = 'hash_456'
        commentary1 = 'AAPL bullish commentary'
        commentary2 = 'AAPL bearish commentary'
        
        # Store different commentary
        test_cache.set_commentary(hash1, commentary1)
        test_cache.set_commentary(hash2, commentary2)
        
        # Verify both are retrievable
        retrieved1 = test_cache.get_commentary(hash1, max_age_hours=24)
        retrieved2 = test_cache.get_commentary(hash2, max_age_hours=24)
        
        assert retrieved1 == commentary1
        assert retrieved2 == commentary2
    
    def test_cache_replacement_with_same_key(self, test_cache, sample_stock_data):
        """Test that storing data with the same key replaces previous data"""
        symbol = 'AAPL'
        period = '1d'
        
        # Store initial data
        test_cache.set_stock_data(symbol, period, sample_stock_data)
        
        # Store new data with same key
        new_data = sample_stock_data.copy()
        new_data['Close'] = [200.0, 201.0, 202.0]
        test_cache.set_stock_data(symbol, period, new_data)
        
        # Verify new data is retrieved
        retrieved_data = test_cache.get_stock_data(symbol, period, max_age_hours=1)
        assert retrieved_data is not None
        pd.testing.assert_frame_equal(retrieved_data, new_data, check_freq=False, check_dtype=False)
        
        # Verify only one entry exists in cache
        if test_cache._connection:
            cursor = test_cache._connection.execute('SELECT COUNT(*) FROM cache WHERE key = ?', (f'stock_{symbol}_{period}',))
            count = cursor.fetchone()[0]
            assert count == 1
        else:
            with sqlite3.connect(test_cache.db_path) as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM cache WHERE key = ?', (f'stock_{symbol}_{period}',))
                count = cursor.fetchone()[0]
                assert count == 1
    
    def test_delete_method(self, test_cache):
        """Test the internal _delete method"""
        # Store some data
        test_cache.set_commentary('test_hash', 'test commentary')
        
        # Verify it exists
        retrieved = test_cache.get_commentary('test_hash', max_age_hours=1)
        assert retrieved == 'test commentary'
        
        # Delete it
        test_cache._delete('commentary_test_hash')
        
        # Verify it's gone
        retrieved = test_cache.get_commentary('test_hash', max_age_hours=1)
        assert retrieved is None
    
    def test_cache_with_config_create_test_config(self):
        """Test cache integration with Config.create_test_config"""
        config = Config.create_test_config()
        cache = SimpleCache(config.db_path)
        
        assert cache.db_path == ':memory:'
        
        # Verify cache works correctly with test config
        cache.set_commentary('test', 'test commentary')
        retrieved = cache.get_commentary('test', max_age_hours=1)
        assert retrieved == 'test commentary'
    
    def test_empty_dataframe_handling(self, test_cache):
        """Test storing and retrieving empty DataFrame"""
        empty_df = pd.DataFrame()
        
        test_cache.set_stock_data('EMPTY', '1d', empty_df)
        retrieved = test_cache.get_stock_data('EMPTY', '1d', max_age_hours=1)
        
        assert retrieved is not None
        assert retrieved.empty
        pd.testing.assert_frame_equal(retrieved, empty_df, check_freq=False, check_dtype=False, 
                                    check_index_type=False, check_column_type=False)
    
    def test_cache_returns_none_for_nonexistent_key(self, test_cache):
        """Test that cache returns None for non-existent keys"""
        # Try to retrieve non-existent stock data
        retrieved_stock = test_cache.get_stock_data('NONEXISTENT', '1d', max_age_hours=1)
        assert retrieved_stock is None
        
        # Try to retrieve non-existent commentary
        retrieved_commentary = test_cache.get_commentary('nonexistent_hash', max_age_hours=1)
        assert retrieved_commentary is None
    
    def test_file_based_cache_operations(self, sample_stock_data):
        """Test cache operations with file-based database"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / 'test_cache.db'
            cache = SimpleCache(str(db_path))
            
            # Test stock data operations
            cache.set_stock_data('TSLA', '1d', sample_stock_data)
            retrieved = cache.get_stock_data('TSLA', '1d', max_age_hours=1)
            assert retrieved is not None
            pd.testing.assert_frame_equal(retrieved, sample_stock_data, check_freq=False, check_dtype=False)
            
            # Test commentary operations
            cache.set_commentary('file_hash', 'File-based commentary')
            commentary = cache.get_commentary('file_hash', max_age_hours=1)
            assert commentary == 'File-based commentary'
            
            # Test cleanup
            deleted = cache.cleanup_old_data(max_age_hours=168)
            assert deleted == 0  # Nothing to delete yet
            
            # Test close method (should be safe to call even for file-based cache)
            cache.close()

    def test_close_method_with_in_memory_cache(self, test_cache):
        """Test the close method with in-memory cache"""
        # Should have a connection for in-memory cache
        assert test_cache._connection is not None
        
        # Close the connection
        test_cache.close()
        
        # Connection should be None after closing
        assert test_cache._connection is None
        
        # Should be safe to call close again
        test_cache.close()
        assert test_cache._connection is None
