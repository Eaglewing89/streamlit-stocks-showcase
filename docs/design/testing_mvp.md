# Testing Strategy MVP

**Simple, Comprehensive Testing for Stock Dashboard Backend**

This testing design aligns with the backend MVP architecture, providing essential test coverage without over-engineering. Tests serve as both quality assurance and living documentation.

## Testing Framework & Structure

- **Framework**: `pytest` with `pytest-mock` for mocking
- **Coverage**: `pytest-cov` for coverage reporting  
- **HTTP Mocking**: `requests-mock` for external API testing
- **Structure**: Organized by test type and component
- **Target Coverage**: 90%+ for core business logic

## Test Organization

```
tests/
├── unit/                           # Fast isolated tests
│   ├── test_config.py             # Configuration validation
│   ├── test_simple_cache.py       # Cache operations
│   ├── test_yfinance_provider.py  # Data fetching logic
│   ├── test_technical_calculator.py # Indicator calculations
│   ├── test_ai_commentary.py      # AI commentary generation
│   └── test_stock_dashboard.py    # Main orchestrator
├── integration/                    # End-to-end workflow tests
│   ├── test_full_analysis.py      # Complete analysis workflow
│   ├── test_cache_integration.py  # Cache + components integration
│   └── test_error_handling.py     # Error scenarios and recovery
├── fixtures/                       # Reusable test data
│   ├── conftest.py                # Global fixtures and config
│   ├── stock_data_fixtures.py     # Sample stock data
│   └── mock_responses.py          # API response mocks
├── factories/                      # Test data generators
│   ├── stock_data_factory.py      # Generate varied stock data
│   └── analysis_factory.py        # Generate analysis scenarios
└── conftest.py                     # Root test configuration
```

## Testing Scope by Component

### 1. Configuration (`test_config.py`)

**Unit Tests:**
- Environment variable validation
- Missing API key handling
- Test configuration creation
- Database path validation

**Key Test Cases:**
```python
def test_config_requires_api_key()
def test_config_with_missing_api_key_raises_error()
def test_config_test_factory_creates_valid_config()
def test_config_defaults_and_overrides()
```

### 2. Simple Cache (`test_simple_cache.py`)

**Unit Tests:**
- Data storage and retrieval
- Cache expiration logic
- Corrupted data handling
- Cleanup operations

**Key Test Cases:**
```python
def test_cache_stores_and_retrieves_stock_data()
def test_cache_respects_expiration_time()
def test_cache_handles_corrupted_dataframe()
def test_cache_commentary_operations()
def test_cleanup_removes_old_entries()
```

### 3. YFinance Provider (`test_yfinance_provider.py`)

**Unit Tests:**
- Data fetching with mocked responses
- Rate limiting behavior
- Symbol validation
- Error handling for invalid symbols

**Key Test Cases:**
```python
def test_fetch_stock_data_success()
def test_fetch_with_invalid_symbol_raises_error()
def test_rate_limiting_delays_requests()
def test_validate_symbol_accepts_valid_symbols()
def test_insufficient_data_handling()
```

### 4. Technical Calculator (`test_technical_calculator.py`)

**Unit Tests:**
- Individual indicator calculations
- Edge cases (insufficient data)
- Trend analysis logic
- Price change calculations

**Key Test Cases:**
```python
def test_sma_calculation_accuracy()
def test_rsi_calculation_accuracy()
def test_insufficient_data_returns_none()
def test_trend_analysis_bullish_bearish_neutral()
def test_price_change_calculation()
def test_calculate_indicators_full_workflow()
```

### 5. AI Commentary Generator (`test_ai_commentary.py`)

**Unit Tests:**
- Prompt generation
- API response handling
- Fallback commentary
- Content hashing for caching
- Rate limiting

**Key Test Cases:**
```python
def test_build_prompt_english_and_swedish()
def test_content_hash_consistency()
def test_fallback_commentary_generation()
def test_rate_limiting_between_api_calls()
def test_api_error_handling()
```

### 6. Stock Dashboard (`test_stock_dashboard.py`)

**Unit Tests:**
- Input validation
- Component orchestration
- Error propagation
- Popular symbols list

**Key Test Cases:**
```python
def test_get_stock_analysis_success_workflow()
def test_symbol_validation()
def test_period_validation()
def test_quick_symbol_validation()
def test_popular_symbols_format()
def test_cache_cleanup_operation()
```

## Integration Tests

### 1. Full Analysis Workflow (`test_full_analysis.py`)

**Integration Tests:**
- Complete analysis pipeline
- Cache utilization across components
- Multi-language commentary
- Different time periods

**Key Test Cases:**
```python
def test_complete_analysis_workflow()
def test_analysis_with_cache_hit()
def test_analysis_with_cache_miss()
def test_multilingual_commentary()
```

### 2. Cache Integration (`test_cache_integration.py`)

**Integration Tests:**
- Cross-component cache usage
- Cache consistency
- Concurrent access handling

**Key Test Cases:**
```python
def test_stock_data_cache_across_requests()
def test_commentary_cache_with_different_languages()
def test_cache_invalidation_after_expiry()
```

### 3. Error Handling (`test_error_handling.py`)

**Integration Tests:**
- Network failures
- API quota exceeded
- Invalid data scenarios
- Graceful degradation

**Key Test Cases:**
```python
def test_network_failure_handling()
def test_api_quota_exceeded_fallback()
def test_invalid_stock_data_handling()
def test_openai_api_failure_fallback()
```

## Test Fixtures and Factories

### Key Fixtures (`conftest.py`)

```python
@pytest.fixture
def test_config():
    """Test configuration with in-memory database"""
    return Config.create_test_config()

@pytest.fixture
def sample_stock_data():
    """Sample AAPL stock data for testing"""
    return create_sample_stock_data('AAPL', days=60)

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return "AAPL is trading at $150.00. Price change: +2.50%. Current trend appears bullish."
```

### Stock Data Factory (`stock_data_factory.py`)

```python
def create_sample_stock_data(symbol='AAPL', days=30, trend='neutral'):
    """Generate realistic stock data for testing"""
    
def create_trending_data(symbol, days, trend_type):
    """Generate data with specific trend patterns"""
    
def create_volatile_data(symbol, days):
    """Generate highly volatile stock data"""
```

## Test Execution Strategy

### Local Development
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests (fast)
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run specific component tests
pytest tests/unit/test_technical_calculator.py -v
```

### CI/CD Pipeline
1. **Unit Tests**: Run on every commit (< 30 seconds)
2. **Integration Tests**: Run on pull requests
3. **Coverage Report**: Generate and check 90% threshold
4. **Performance Tests**: Basic timing checks for key operations

## Mock Strategy

### External Dependencies
- **YFinance API**: Mock with `requests-mock` or `pytest-mock`
- **OpenAI API**: Mock responses for different scenarios
- **File System**: Use in-memory SQLite for cache tests

### Internal Dependencies
- **Time-based operations**: Mock `time.time()` for cache tests
- **Random operations**: Set seeds for reproducible test data

## Test Data Management

### Static Test Data
- Sample stock data files (JSON/CSV)
- Expected calculation results
- API response examples

### Dynamic Test Data
- Generated using factories
- Parameterized tests for multiple scenarios
- Edge case generation

## Testing Benefits

1. **Fast Feedback**: Unit tests complete in seconds
2. **Comprehensive Coverage**: Tests all critical paths and edge cases
3. **Documentation**: Tests demonstrate expected behavior and usage
4. **Refactoring Safety**: Enables confident code changes
5. **Bug Prevention**: Catches regressions early
6. **Integration Confidence**: Validates component interactions

## Test Maintenance Guidelines

1. **Keep Tests Simple**: Each test focuses on one behavior
2. **Use Descriptive Names**: Test names explain what's being tested
3. **Minimize Setup**: Use fixtures to reduce test boilerplate
4. **Test Edge Cases**: Include boundary conditions and error scenarios
5. **Regular Review**: Update tests when requirements change

This testing strategy provides comprehensive coverage while remaining practical for rapid development. The separation of unit and integration tests allows for fast feedback during development while ensuring system-level reliability.