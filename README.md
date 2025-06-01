# Streamlit Stock Dashboard

A modern, interactive stock dashboard built with Streamlit that provides real-time stock analysis, technical indicators, and AI-powered market commentary.

## Features

- **Real-time Stock Data**: Fetches current stock prices and historical data using Yahoo Finance
- **Technical Analysis**: Calculates key indicators including SMA, RSI, and trend analysis
- **AI Commentary**: Generates intelligent market commentary using OpenAI's GPT models
- **Interactive Charts**: Beautiful, responsive charts using Plotly
- **Multi-language Support**: Commentary available in English and Swedish
- **Smart Caching**: Efficient data caching to minimize API calls

## Project Structure

```
stock-dashboard/
├── src/                    # Backend source code
│   ├── config.py          # Configuration management
│   ├── cache/             # Data caching layer
│   ├── data/              # Stock data providers
│   ├── analysis/          # Technical analysis
│   └── ai/                # AI commentary generation
├── streamlit/             # Frontend application
│   ├── app.py            # Main Streamlit app
│   ├── components/       # Reusable UI components
│   └── utils/            # Frontend utilities
├── tests/                # Test suite
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   ├── fixtures/        # Test data
│   └── factories/       # Test data generators
├── data/                # Data storage
└── docs/                # Documentation
```

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (for AI commentary feature)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd streamlit-stocks-showcase
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Linux/macOS:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   
   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   DB_PATH=data/cache.db
   CACHE_HOURS=1
   ```

## Running the Application

1. **Start the Streamlit application:**
   ```bash
   streamlit run streamlit/app.py
   ```

2. **Open your browser:**
   The application will automatically open at `http://localhost:8501`

## Usage

1. **Select a Stock**: Choose from popular stocks or enter a custom symbol
2. **Choose Time Period**: Select from 1 day to 1 year of historical data
3. **View Analysis**: See real-time price, technical indicators, and trend analysis
4. **Read Commentary**: Get AI-generated insights about the stock's performance
5. **Interactive Charts**: Explore price movements and technical indicators

## Configuration

The application can be configured through environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DB_PATH`: Path to SQLite cache database (default: `data/cache.db`)
- `CACHE_HOURS`: Cache expiration time in hours (default: `1`)

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/
```

## Development

### Code Style
This project follows standard Python formatting and linting practices. Key guidelines:

- Use descriptive variable and function names
- Add docstrings to all classes and functions
- Keep functions focused and modular
- Handle errors gracefully with appropriate error messages

### Adding New Features

1. **Backend Components**: Add new modules under `src/`
2. **Frontend Components**: Add reusable UI components under `streamlit/components/`
3. **Tests**: Write corresponding tests in `tests/unit/` and `tests/integration/`

## Future Development Ideas

### Short-term Improvements
- **Portfolio Tracking**: Allow users to track multiple stocks and build watchlists
- **More Technical Indicators**: Add MACD, Bollinger Bands, volume analysis
- **Alert System**: Email/SMS notifications for significant price movements
- **Data Export**: Export analysis results to CSV/PDF formats

### Long-term Enhancements
- **Sentiment Analysis**: Integrate news sentiment analysis with stock prices
- **Backtesting Framework**: Test trading strategies against historical data
- **Machine Learning Models**: Predict stock movements using ML algorithms
- **Real-time Updates**: Live price feeds with automatic chart updates
- **Social Features**: Share analyses and insights with other users

## Technical Architecture

### Backend (MVP)
- **Configuration Management**: Simple environment-based configuration
- **Data Provider**: Yahoo Finance integration with rate limiting
- **Technical Calculator**: Essential indicators (SMA, RSI, trend analysis)
- **AI Commentary**: OpenAI integration with fallback commentary
- **Caching Layer**: SQLite-based caching for performance optimization

### Frontend (Streamlit)
- **Main Application**: Clean, professional dashboard interface
- **Interactive Components**: Real-time charts and user controls
- **Error Handling**: Graceful degradation and user-friendly error messages
- **Performance**: Optimized loading and caching strategies

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is for educational purposes as part of a programming assignment.

## Troubleshooting

### Common Issues

**"OPENAI_API_KEY environment variable is required"**
- Ensure you have set the `OPENAI_API_KEY` in your `.env` file
- Verify the `.env` file is in the project root directory

**"No data found for symbol"**
- Check that the stock symbol is valid and correctly spelled
- Some symbols may not be available on Yahoo Finance

**Slow performance**
- The application caches data to improve performance
- Initial requests may be slower due to data fetching and processing

**Chart not displaying**
- Ensure all dependencies are installed correctly
- Check browser console for JavaScript errors

For additional help, please check the documentation in the `docs/` directory or create an issue in the repository.
