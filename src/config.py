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
