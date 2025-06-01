import pytest
import time
import hashlib
import json
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from src.ai.commentary_generator import AICommentaryGenerator


@pytest.fixture
def sample_indicators():
    """Sample technical indicators for testing"""
    return {
        'current_price': 150.25,
        'sma_20': 148.50,
        'sma_50': 145.00,
        'rsi': 65.2,
        'trend': 'bullish',
        'price_change_1d': {'percent': 2.5, 'absolute': 3.75}
    }


@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing"""
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    data = pd.DataFrame({
        'Open': [150.0] * 30,
        'High': [155.0] * 30,
        'Low': [145.0] * 30,
        'Close': [150.25] * 30,
        'Volume': [1000000] * 30
    }, index=dates)
    return data


@pytest.fixture
def ai_generator():
    """AI commentary generator instance for testing"""
    return AICommentaryGenerator("test_api_key")


class TestAICommentaryGenerator:
    """Test suite for AICommentaryGenerator class"""

    def test_init_creates_openai_client(self):
        """Test that initialization creates OpenAI client with API key"""
        api_key = "test_api_key_123"
        generator = AICommentaryGenerator(api_key)
        
        assert generator.client is not None
        assert generator.min_interval == 2.0
        assert generator.last_call_time == 0

    def test_build_prompt_english(self, ai_generator, sample_indicators):
        """Test prompt building for English commentary"""
        prompt = ai_generator._build_prompt("AAPL", sample_indicators, "1mo", "en")
        
        assert "Generate a professional market commentary in English" in prompt
        assert "AAPL" in prompt
        assert "this month" in prompt
        assert "$150.25" in prompt
        assert "$148.50" in prompt  # SMA 20
        assert "65.2" in prompt     # RSI (exact value)
        assert "bullish" in prompt
        assert "2.50%" in prompt    # Price change
        assert "Provide 2-3 sentences" in prompt
        assert "avoid direct investment advice" in prompt

    def test_build_prompt_swedish(self, ai_generator, sample_indicators):
        """Test prompt building for Swedish commentary"""
        prompt = ai_generator._build_prompt("AAPL", sample_indicators, "3mo", "sv")
        
        assert "Generera en professionell marknadskommentar på svenska" in prompt
        assert "AAPL" in prompt
        assert "this quarter" in prompt
        assert "$150.25" in prompt

    def test_build_prompt_different_periods(self, ai_generator, sample_indicators):
        """Test prompt building for different time periods"""
        test_cases = [
            ("1d", "today's trading"),
            ("5d", "this week"),
            ("1mo", "this month"),
            ("3mo", "this quarter"),
            ("6mo", "6 months"),
            ("1y", "this year"),
            ("2y", "the 2y period")  # Default case
        ]
        
        for period, expected_context in test_cases:
            prompt = ai_generator._build_prompt("AAPL", sample_indicators, period, "en")
            assert expected_context in prompt

    def test_create_content_hash_consistency(self, ai_generator, sample_indicators):
        """Test that content hash is consistent for same inputs"""
        hash1 = ai_generator._create_content_hash("AAPL", sample_indicators, "1mo", "en")
        hash2 = ai_generator._create_content_hash("AAPL", sample_indicators, "1mo", "en")
        
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length
        assert isinstance(hash1, str)

    def test_create_content_hash_different_inputs(self, ai_generator, sample_indicators):
        """Test that different inputs produce different hashes"""
        hash1 = ai_generator._create_content_hash("AAPL", sample_indicators, "1mo", "en")
        hash2 = ai_generator._create_content_hash("GOOGL", sample_indicators, "1mo", "en")
        hash3 = ai_generator._create_content_hash("AAPL", sample_indicators, "3mo", "en")
        hash4 = ai_generator._create_content_hash("AAPL", sample_indicators, "1mo", "sv")
        
        assert hash1 != hash2  # Different symbol
        assert hash1 != hash3  # Different period
        assert hash1 != hash4  # Different language

    def test_create_content_hash_rounded_values(self, ai_generator):
        """Test that hash uses rounded values for stability"""
        indicators1 = {
            'current_price': 150.254,
            'rsi': 65.23,
            'trend': 'bullish',
            'price_change_1d': {'percent': 2.54}
        }
        
        indicators2 = {
            'current_price': 150.256,  # Slight difference, but rounds to same value (150.25)
            'rsi': 65.73,              # Different enough to round differently (65 vs 66)
            'trend': 'bullish',
            'price_change_1d': {'percent': 2.56}  # Slight difference, rounds to same (2.5)
        }
        
        hash1 = ai_generator._create_content_hash("AAPL", indicators1, "1mo", "en")
        hash2 = ai_generator._create_content_hash("AAPL", indicators2, "1mo", "en")
        
        # Should be different due to RSI rounding differently (65 vs 66)
        assert hash1 != hash2
        
        # Test with values that actually round to the same
        indicators3 = {
            'current_price': 150.251,  # Rounds to 150.25
            'rsi': 65.23,              # Rounds to 65
            'trend': 'bullish',
            'price_change_1d': {'percent': 2.52}  # Rounds to 2.5
        }
        
        indicators4 = {
            'current_price': 150.254,  # Rounds to 150.25 (same)
            'rsi': 65.27,              # Rounds to 65 (same)
            'trend': 'bullish',
            'price_change_1d': {'percent': 2.54}  # Rounds to 2.5 (same)
        }
        
        hash3 = ai_generator._create_content_hash("AAPL", indicators3, "1mo", "en")
        hash4 = ai_generator._create_content_hash("AAPL", indicators4, "1mo", "en")
        
        # These should be the same due to rounding
        assert hash3 == hash4

    def test_get_fallback_commentary_english(self, ai_generator, sample_indicators):
        """Test fallback commentary generation in English"""
        commentary = ai_generator._get_fallback_commentary("AAPL", sample_indicators, "1mo", "en")
        
        assert "AAPL is trading at $150.25" in commentary
        assert "+2.50%" in commentary
        assert "bullish" in commentary
        assert isinstance(commentary, str)
        assert len(commentary) > 0

    def test_get_fallback_commentary_swedish(self, ai_generator, sample_indicators):
        """Test fallback commentary generation in Swedish"""
        commentary = ai_generator._get_fallback_commentary("AAPL", sample_indicators, "1mo", "sv")
        
        assert "AAPL handlas för $150.25" in commentary
        assert "+2.50%" in commentary
        assert "bullish" in commentary
        assert isinstance(commentary, str)

    def test_get_fallback_commentary_unknown_language(self, ai_generator, sample_indicators):
        """Test fallback commentary defaults to English for unknown language"""
        commentary = ai_generator._get_fallback_commentary("AAPL", sample_indicators, "1mo", "fr")
        
        # Should default to English
        assert "AAPL is trading at $150.25" in commentary
        assert "handlas för" not in commentary  # Should not be Swedish

    def test_get_fallback_commentary_missing_indicators(self, ai_generator):
        """Test fallback commentary with missing indicator values"""
        incomplete_indicators = {
            'current_price': 100.0,
            # Missing other indicators
        }
        
        commentary = ai_generator._get_fallback_commentary("TEST", incomplete_indicators, "1mo", "en")
        
        assert "TEST is trading at $100.00" in commentary
        assert "+0.00%" in commentary  # Default value
        assert "neutral" in commentary  # Default trend

    @patch('src.ai.commentary_generator.time.time')
    def test_rate_limiting_delays_requests(self, mock_time, ai_generator, sample_indicators, sample_stock_data):
        """Test that rate limiting enforces minimum interval between API calls"""
        # Mock time progression: first call for elapsed calculation, second for updating last_call_time
        mock_time.side_effect = [1001.0, 1003.0]  # 1 second elapsed, then after sleep
        
        with patch.object(ai_generator.client.chat.completions, 'create') as mock_create, \
             patch('src.ai.commentary_generator.time.sleep') as mock_sleep:
            
            mock_create.return_value = Mock()
            mock_create.return_value.choices = [Mock()]
            mock_create.return_value.choices[0].message.content = "Test commentary"
            
            # Set last call time to simulate previous call
            ai_generator.last_call_time = 1000.0
            
            ai_generator.generate_commentary("AAPL", sample_stock_data, sample_indicators, "1mo", "en")
            
            # Should sleep for (2.0 - 1.0) = 1.0 second
            mock_sleep.assert_called_once_with(1.0)

    @patch('src.ai.commentary_generator.time.time')
    def test_rate_limiting_no_delay_when_sufficient_time_passed(self, mock_time, ai_generator, sample_indicators, sample_stock_data):
        """Test that no delay occurs when sufficient time has passed"""
        mock_time.return_value = 1005.0  # 5 seconds later
        
        with patch.object(ai_generator.client.chat.completions, 'create') as mock_create, \
             patch('src.ai.commentary_generator.time.sleep') as mock_sleep:
            
            mock_create.return_value = Mock()
            mock_create.return_value.choices = [Mock()]
            mock_create.return_value.choices[0].message.content = "Test commentary"
            
            ai_generator.last_call_time = 1000.0  # 5 seconds ago
            
            ai_generator.generate_commentary("AAPL", sample_stock_data, sample_indicators, "1mo", "en")
            
            # Should not sleep since 5 seconds > 2 seconds minimum interval
            mock_sleep.assert_not_called()

    @patch('src.ai.commentary_generator.time.time')
    def test_generate_commentary_successful_api_call(self, mock_time, ai_generator, sample_indicators, sample_stock_data):
        """Test successful OpenAI API call"""
        mock_time.return_value = 1000.0
        
        with patch.object(ai_generator.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "  AAPL shows strong momentum with bullish indicators.  "
            mock_create.return_value = mock_response
            
            result = ai_generator.generate_commentary("AAPL", sample_stock_data, sample_indicators, "1mo", "en")
            
            assert result == "AAPL shows strong momentum with bullish indicators."  # Stripped
            mock_create.assert_called_once()
            
            # Verify API call parameters
            call_args = mock_create.call_args
            assert call_args[1]['model'] == "gpt-3.5-turbo"
            assert call_args[1]['max_tokens'] == 200
            assert call_args[1]['temperature'] == 0.7
            assert len(call_args[1]['messages']) == 1
            assert call_args[1]['messages'][0]['role'] == "user"

    def test_generate_commentary_api_failure_fallback(self, ai_generator, sample_indicators, sample_stock_data):
        """Test that API failure triggers fallback commentary"""
        with patch.object(ai_generator.client.chat.completions, 'create') as mock_create:
            mock_create.side_effect = Exception("API Error")
            
            result = ai_generator.generate_commentary("AAPL", sample_stock_data, sample_indicators, "1mo", "en")
            
            # Should return fallback commentary
            assert "AAPL is trading at $150.25" in result
            assert "+2.50%" in result
            assert "bullish" in result

    def test_generate_commentary_api_none_content_fallback(self, ai_generator, sample_indicators, sample_stock_data):
        """Test that API returning None content triggers fallback commentary"""
        with patch.object(ai_generator.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = None  # OpenAI returns None content
            mock_create.return_value = mock_response
            
            result = ai_generator.generate_commentary("AAPL", sample_stock_data, sample_indicators, "1mo", "en")
            
            # Should return fallback commentary
            assert "AAPL is trading at $150.25" in result
            assert "+2.50%" in result
            assert "bullish" in result

    def test_generate_commentary_updates_last_call_time(self, ai_generator, sample_indicators, sample_stock_data):
        """Test that last_call_time is updated after API call"""
        with patch.object(ai_generator.client.chat.completions, 'create') as mock_create, \
             patch('src.ai.commentary_generator.time.time') as mock_time:
            
            mock_create.return_value = Mock()
            mock_create.return_value.choices = [Mock()]
            mock_create.return_value.choices[0].message.content = "Test commentary"
            mock_time.return_value = 1234.5
            
            initial_time = ai_generator.last_call_time
            ai_generator.generate_commentary("AAPL", sample_stock_data, sample_indicators, "1mo", "en")
            
            assert ai_generator.last_call_time == 1234.5
            assert ai_generator.last_call_time != initial_time

    def test_generate_commentary_builds_correct_prompt(self, ai_generator, sample_indicators, sample_stock_data):
        """Test that generate_commentary uses the correct prompt"""
        with patch.object(ai_generator.client.chat.completions, 'create') as mock_create, \
             patch.object(ai_generator, '_build_prompt') as mock_build_prompt:
            
            mock_create.return_value = Mock()
            mock_create.return_value.choices = [Mock()]
            mock_create.return_value.choices[0].message.content = "Test commentary"
            mock_build_prompt.return_value = "test prompt"
            
            ai_generator.generate_commentary("AAPL", sample_stock_data, sample_indicators, "3mo", "sv")
            
            mock_build_prompt.assert_called_once_with("AAPL", sample_indicators, "3mo", "sv")
            
            # Verify the prompt was used in the API call
            call_args = mock_create.call_args
            assert call_args[1]['messages'][0]['content'] == "test prompt"

    def test_multiple_language_support(self, ai_generator, sample_indicators):
        """Test that both English and Swedish are properly supported"""
        # Test English
        fallback_en = ai_generator._get_fallback_commentary("AAPL", sample_indicators, "1mo", "en")
        assert "is trading at" in fallback_en
        
        # Test Swedish
        fallback_sv = ai_generator._get_fallback_commentary("AAPL", sample_indicators, "1mo", "sv")
        assert "handlas för" in fallback_sv
        
        # Different content for different languages
        assert fallback_en != fallback_sv

    def test_prompt_includes_all_required_indicators(self, ai_generator, sample_indicators):
        """Test that prompt includes all technical indicators"""
        prompt = ai_generator._build_prompt("AAPL", sample_indicators, "1mo", "en")
        
        # Check all required indicators are present
        assert "Current Price: $150.25" in prompt
        assert "20-day SMA: $148.50" in prompt
        assert "50-day SMA: $145.00" in prompt
        assert "RSI: 65.2" in prompt
        assert "Trend: bullish" in prompt
        assert "Price Change: 2.50%" in prompt
