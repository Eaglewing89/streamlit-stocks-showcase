import os
import pytest
from unittest.mock import patch
from src.config import Config


class TestConfig:
    """Test suite for the Config class"""
    
    def test_config_requires_api_key(self):
        """Test that Config raises error when OPENAI_API_KEY is missing"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is required"):
                Config()
    
    def test_config_with_valid_api_key(self):
        """Test that Config initializes successfully with valid API key"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            config = Config()
            assert config.openai_api_key == 'test_key'
            assert config.db_path == 'data/cache.db'  # default value
            assert config.cache_hours == 1  # default value
    
    def test_config_defaults_and_overrides(self):
        """Test default values and environment variable overrides"""
        env_vars = {
            'OPENAI_API_KEY': 'my_api_key',
            'DB_PATH': 'custom/path/cache.db',
            'CACHE_HOURS': '24'
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            assert config.openai_api_key == 'my_api_key'
            assert config.db_path == 'custom/path/cache.db'
            assert config.cache_hours == 24
    
    def test_config_cache_hours_conversion(self):
        """Test that CACHE_HOURS is properly converted to integer"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key', 'CACHE_HOURS': '12'}):
            config = Config()
            assert config.cache_hours == 12
            assert isinstance(config.cache_hours, int)
    
    def test_config_test_factory_creates_valid_config(self):
        """Test that create_test_config factory method works correctly"""
        config = Config.create_test_config()
        
        assert config.openai_api_key == 'test_key'
        assert config.db_path == ':memory:'
        assert config.cache_hours == 1
    
    def test_config_test_factory_with_custom_key(self):
        """Test create_test_config with custom API key"""
        custom_key = 'custom_test_key'
        config = Config.create_test_config(openai_key=custom_key)
        
        assert config.openai_api_key == custom_key
        assert config.db_path == ':memory:'
        assert config.cache_hours == 1
    
    def test_config_with_missing_api_key_raises_error(self):
        """Test specific error message for missing API key"""
        # Clear all environment variables to ensure OPENAI_API_KEY is not set
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config()
            
            assert "OPENAI_API_KEY environment variable is required" in str(exc_info.value)
    
    def test_config_empty_api_key_raises_error(self):
        """Test that empty API key raises error"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': ''}):
            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is required"):
                Config()
    
    def test_config_none_api_key_raises_error(self):
        """Test that None API key raises error"""
        with patch.dict(os.environ, {}, clear=True):
            # Explicitly set to None for OPENAI_API_KEY only
            with patch('os.getenv') as mock_getenv:
                def mock_getenv_side_effect(key, default=None):
                    if key == 'OPENAI_API_KEY':
                        return None
                    elif key == 'DB_PATH':
                        return default
                    elif key == 'CACHE_HOURS':
                        return default
                    return default
                
                mock_getenv.side_effect = mock_getenv_side_effect
                with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is required"):
                    Config()
    
    def test_config_db_path_default(self):
        """Test default database path when DB_PATH not set"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}, clear=True):
            config = Config()
            assert config.db_path == 'data/cache.db'
    
    def test_config_cache_hours_default(self):
        """Test default cache hours when CACHE_HOURS not set"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}, clear=True):
            config = Config()
            assert config.cache_hours == 1
