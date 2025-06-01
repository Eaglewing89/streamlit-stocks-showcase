# Frontend MVP Design - Streamlit Stock Dashboard

**Clean, Professional, High-Performance Financial Dashboard**

## Overview

This frontend design document outlines a Streamlit-based stock dashboard that seamlessly integrates with our backend MVP architecture. The design prioritizes simplicity, performance, and professional presentation while maintaining extensibility for future enhancements.

## Design Principles

- **Performance First**: Efficient data loading with smart caching
- **Clean Interface**: Professional financial dashboard aesthetics
- **User-Centric**: Intuitive navigation and clear information hierarchy
- **Responsive Design**: Works well on different screen sizes
- **Error Resilience**: Graceful handling of backend errors
- **Backend Integration**: Seamless coordination with StockDashboard orchestrator

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit App (app.py)                   │
│  - Session state management                                 │
│  - Page layout coordination                                 │
│  - Error boundary handling                                  │
└─────┬─────────┬──────────────┬─────────────────────────────┘
      │         │              │
┌──── ▼ ───┐ ┌─ ▼ ──────┐ ┌─── ▼ ────┐
│Sidebar   │ │Chart     │ │Display   │
│Controls  │ │Components│ │Components│
│          │ │          │ │          │
└──────────┘ └──────────┘ └──────────┘
      │         │              │
┌──── ▼ ────────▼──────────────▼──────┐
│         Utility Functions            │
│      (formatters, validators)        │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│        Backend Integration          │
│         (StockDashboard)            │
└─────────────────────────────────────┘
```

## File Structure

```
streamlit/
├── app.py                          # Main Streamlit application
├── components/                     # Reusable UI components
│   ├── __init__.py
│   ├── sidebar.py                  # User controls and settings
│   ├── charts.py                   # Chart visualizations
│   ├── display.py                  # Data display components
│   ├── metrics.py                  # Key metrics display
│   └── errors.py                   # Error handling components
├── utils/                          # Utility functions
│   ├── __init__.py
│   ├── formatters.py              # Data formatting utilities
│   ├── validators.py              # Input validation
│   └── session.py                 # Session state management
└── config/
    ├── __init__.py
    └── ui_config.py               # UI configuration constants
```

## Core Components Design

### 1. Main Application (`app.py`)

**Key Responsibilities:**
- Page configuration and layout
- Session state initialization
- Component orchestration
- Global error handling
- Backend integration coordination

**Performance Features:**
- Smart data caching with TTL
- Lazy loading of expensive operations
- Efficient component updates
- Memory management for large datasets

```python
# Main application structure (simplified)
import streamlit as st
from src.dashboard import StockDashboard
from components import sidebar, charts, display, metrics, errors
from utils import session, formatters

def main():
    # Page configuration
    st.set_page_config(
        page_title="Stock Dashboard",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state and backend
    session.initialize_session()
    dashboard = get_dashboard_instance()
    
    # Render UI components
    render_header()
    symbol, period, language = sidebar.render_controls()
    
    if symbol:
        with st.spinner("Loading analysis..."):
            render_analysis(dashboard, symbol, period, language)
    else:
        render_welcome_screen()

def render_analysis(dashboard, symbol, period, language):
    try:
        # Get analysis data (cached automatically by backend)
        analysis = dashboard.get_stock_analysis(symbol, period, language)
        
        # Render components in layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            charts.render_price_chart(analysis['data'], analysis['indicators'])
            charts.render_indicators_chart(analysis['indicators'])
        
        with col2:
            metrics.render_key_metrics(analysis['indicators'])
            display.render_ai_commentary(analysis['commentary'])
            display.render_technical_summary(analysis['indicators'])
            
    except Exception as e:
        errors.handle_analysis_error(e, symbol)
```

### 2. Sidebar Controls (`components/sidebar.py`)

**Features:**
- Stock symbol input with validation
- Time period selection
- Language toggle (English/Swedish)
- Popular stocks quick selection
- Settings and preferences

**User Experience:**
- Real-time symbol validation
- Autocomplete suggestions
- Clear error messaging
- Responsive design

```python
def render_controls():
    """Render sidebar controls and return user selections"""
    
    st.sidebar.title("📈 Stock Dashboard")
    
    # Symbol input with validation
    symbol = render_symbol_input()
    
    # Time period selection
    period = st.sidebar.selectbox(
        "Time Period",
        options=['1d', '5d', '1mo', '3mo', '6mo', '1y'],
        index=2,  # Default to 1mo
        format_func=format_period_display
    )
    
    # Language selection
    language = st.sidebar.radio(
        "Language",
        options=['en', 'sv'],
        format_func=lambda x: '🇺🇸 English' if x == 'en' else '🇸🇪 Svenska'
    )
    
    # Popular stocks quick selection
    render_popular_stocks()
    
    # Additional settings
    render_settings_section()
    
    return symbol, period, language

def render_symbol_input():
    """Stock symbol input with validation"""
    symbol = st.sidebar.text_input(
        "Stock Symbol",
        value=st.session_state.get('symbol', ''),
        placeholder="e.g., AAPL, GOOGL",
        help="Enter a valid stock ticker symbol"
    ).upper()
    
    if symbol and len(symbol) > 0:
        # Real-time validation
        if validators.is_valid_symbol_format(symbol):
            st.sidebar.success(f"✓ {symbol}")
        else:
            st.sidebar.error("❌ Invalid symbol format")
            return None
    
    return symbol if symbol else None
```

### 3. Chart Components (`components/charts.py`)

**Chart Types:**
- Price chart with moving averages
- Volume chart
- Technical indicators chart
- Trend analysis visualization

**Technology Stack:**
- Plotly for interactive charts
- Optimized for performance
- Mobile-responsive design
- Professional financial styling

```python
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def render_price_chart(data, indicators):
    """Render main price chart with indicators"""
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=('Price & Moving Averages', 'Volume'),
        row_width=[0.7, 0.3]
    )
    
    # Price candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="Price"
        ),
        row=1, col=1
    )
    
    # Moving averages
    if indicators.get('sma_20'):
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=calculate_sma_series(data['Close'], 20),
                name="SMA 20",
                line=dict(color='orange', width=2)
            ),
            row=1, col=1
        )
    
    if indicators.get('sma_50'):
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=calculate_sma_series(data['Close'], 50),
                name="SMA 50",
                line=dict(color='red', width=2)
            ),
            row=1, col=1
        )
    
    # Volume chart
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['Volume'],
            name="Volume",
            marker_color='lightblue'
        ),
        row=2, col=1
    )
    
    # Professional styling
    fig.update_layout(
        title=f"Stock Price Analysis",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        template="plotly_white",
        showlegend=True,
        height=600
    )
    
    fig.update_xaxes(rangeslider_visible=False)
    
    st.plotly_chart(fig, use_container_width=True)

def render_indicators_chart(indicators):
    """Render technical indicators in a separate chart"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # RSI Gauge
        render_rsi_gauge(indicators.get('rsi'))
    
    with col2:
        # Trend indicator
        render_trend_indicator(indicators.get('trend'))
```

### 4. Display Components (`components/display.py`)

**Components:**
- AI commentary display
- Technical analysis summary
- Key statistics table
- Last updated timestamp

**Design Features:**
- Clean typography
- Proper spacing and hierarchy
- Color-coded indicators
- Mobile-friendly layout

```python
def render_ai_commentary(commentary):
    """Display AI-generated market commentary"""
    
    st.subheader("🤖 Market Analysis")
    
    # Commentary box with proper styling
    st.markdown(
        f"""
        <div style="
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
        ">
            <p style="margin: 0; line-height: 1.6;">
                {commentary}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_technical_summary(indicators):
    """Display technical analysis summary"""
    
    st.subheader("📊 Technical Summary")
    
    # Create summary table
    summary_data = {
        "Indicator": ["Current Price", "20-Day SMA", "50-Day SMA", "RSI", "Trend"],
        "Value": [
            f"${indicators.get('current_price', 0):.2f}",
            f"${indicators.get('sma_20', 0):.2f}" if indicators.get('sma_20') else "N/A",
            f"${indicators.get('sma_50', 0):.2f}" if indicators.get('sma_50') else "N/A",
            f"{indicators.get('rsi', 0):.1f}" if indicators.get('rsi') else "N/A",
            format_trend_display(indicators.get('trend', 'neutral'))
        ],
        "Signal": [
            get_price_signal(indicators),
            get_sma_signal(indicators, 20),
            get_sma_signal(indicators, 50),
            get_rsi_signal(indicators.get('rsi')),
            get_trend_signal(indicators.get('trend'))
        ]
    }
    
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)
```

### 5. Metrics Components (`components/metrics.py`)

**Key Metrics Display:**
- Current price with change indicators
- Volume metrics
- Performance metrics
- Technical indicator status

```python
def render_key_metrics(indicators):
    """Render key metrics in an attractive layout"""
    
    st.subheader("📈 Key Metrics")
    
    # Top row - Price metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_price = indicators.get('current_price', 0)
        st.metric(
            label="Current Price",
            value=f"${current_price:.2f}",
            delta=format_price_change(indicators.get('price_change_1d', {}))
        )
    
    with col2:
        volume = indicators.get('volume_avg', 0)
        st.metric(
            label="Avg Volume (20d)",
            value=formatters.format_volume(volume)
        )
    
    with col3:
        rsi = indicators.get('rsi')
        if rsi:
            st.metric(
                label="RSI (14)",
                value=f"{rsi:.1f}",
                delta=get_rsi_status(rsi)
            )
    
    # Second row - Moving averages
    col4, col5, col6 = st.columns(3)
    
    with col4:
        sma_20 = indicators.get('sma_20')
        if sma_20:
            st.metric(
                label="SMA 20",
                value=f"${sma_20:.2f}",
                delta=get_sma_vs_price_status(indicators.get('current_price'), sma_20)
            )
    
    with col5:
        sma_50 = indicators.get('sma_50')
        if sma_50:
            st.metric(
                label="SMA 50",
                value=f"${sma_50:.2f}",
                delta=get_sma_vs_price_status(indicators.get('current_price'), sma_50)
            )
    
    with col6:
        trend = indicators.get('trend', 'neutral')
        st.metric(
            label="Trend",
            value=format_trend_display(trend),
            delta=get_trend_status(trend)
        )
```

### 6. Error Handling (`components/errors.py`)

**Error Types:**
- Invalid symbol errors
- API timeout errors
- Data unavailable errors
- Backend service errors

**Error Display:**
- User-friendly error messages
- Actionable suggestions
- Fallback content when possible

```python
def handle_analysis_error(error, symbol):
    """Handle and display analysis errors gracefully"""
    
    error_type = classify_error(error)
    
    if error_type == 'invalid_symbol':
        st.error(f"❌ Symbol '{symbol}' not found or invalid")
        st.info("💡 Try a different symbol or check the spelling")
        render_popular_symbols_suggestion()
        
    elif error_type == 'api_timeout':
        st.warning("⏱️ Data loading took longer than expected")
        st.info("🔄 Please try again in a moment")
        
    elif error_type == 'insufficient_data':
        st.warning(f"📊 Insufficient data for {symbol}")
        st.info("💡 Try a longer time period or different symbol")
        
    else:
        st.error("❌ An unexpected error occurred")
        st.info("🔄 Please refresh the page or try again")
        
        # Show error details in expander for debugging
        with st.expander("Error Details"):
            st.code(str(error))

def render_popular_symbols_suggestion():
    """Show popular symbols when user enters invalid symbol"""
    
    st.markdown("**Popular symbols to try:**")
    
    popular = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META']
    
    cols = st.columns(len(popular))
    for i, symbol in enumerate(popular):
        with cols[i]:
            if st.button(symbol, key=f"suggest_{symbol}"):
                st.session_state.symbol = symbol
                st.experimental_rerun()
```

## Utility Functions

### 1. Formatters (`utils/formatters.py`)

**Formatting Functions:**
- Currency formatting
- Volume formatting  
- Percentage formatting
- Date/time formatting
- Number abbreviations (K, M, B)

```python
def format_currency(value, decimals=2):
    """Format currency values with proper symbols"""
    if value is None:
        return "N/A"
    return f"${value:,.{decimals}f}"

def format_volume(volume):
    """Format volume with appropriate abbreviations"""
    if volume >= 1_000_000_000:
        return f"{volume/1_000_000_000:.1f}B"
    elif volume >= 1_000_000:
        return f"{volume/1_000_000:.1f}M"
    elif volume >= 1_000:
        return f"{volume/1_000:.1f}K"
    else:
        return f"{volume:.0f}"

def format_percentage(value, decimals=2, include_sign=True):
    """Format percentage values"""
    if value is None:
        return "N/A"
    
    sign = "+" if value > 0 and include_sign else ""
    return f"{sign}{value:.{decimals}f}%"

def format_period_display(period):
    """Convert period codes to user-friendly labels"""
    periods = {
        '1d': '1 Day',
        '5d': '5 Days', 
        '1mo': '1 Month',
        '3mo': '3 Months',
        '6mo': '6 Months',
        '1y': '1 Year'
    }
    return periods.get(period, period)
```

### 2. Session Management (`utils/session.py`)

**Session State Management:**
- User preferences
- Last viewed symbols
- Cache management
- Error state tracking

```python
def initialize_session():
    """Initialize session state with defaults"""
    
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.symbol = ''
        st.session_state.period = '1mo'
        st.session_state.language = 'en'
        st.session_state.last_symbols = []
        st.session_state.preferences = {
            'chart_height': 600,
            'show_volume': True,
            'show_indicators': True
        }

def update_symbol_history(symbol):
    """Track recently viewed symbols"""
    if 'last_symbols' not in st.session_state:
        st.session_state.last_symbols = []
    
    if symbol and symbol not in st.session_state.last_symbols:
        st.session_state.last_symbols.insert(0, symbol)
        # Keep only last 5 symbols
        st.session_state.last_symbols = st.session_state.last_symbols[:5]

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_analysis(symbol, period, language):
    """Cache wrapper for analysis data"""
    # This leverages Streamlit's caching on top of backend caching
    dashboard = get_dashboard_instance()
    return dashboard.get_stock_analysis(symbol, period, language)
```

## Performance Optimization

### 1. Caching Strategy

**Multi-Level Caching:**
- Backend cache (SQLite) - 1 hour TTL for data
- Streamlit cache - 5 minutes TTL for UI
- Browser cache - Static assets

**Cache Invalidation:**
- Time-based expiration
- Manual refresh option
- Smart cache warming for popular symbols

### 2. Lazy Loading

**Techniques:**
- Load charts only when symbol is selected
- Progressive data loading for large datasets
- Component-level loading states

### 3. Memory Management

**Optimization:**
- Efficient DataFrame operations
- Minimal data duplication
- Garbage collection for old session data

## UI/UX Design Guidelines

### 1. Color Scheme

**Primary Colors:**
- Blue (#1f77b4) - Primary actions, links
- Green (#2ca02c) - Positive values, gains
- Red (#d62728) - Negative values, losses
- Gray (#7f7f7f) - Neutral, secondary text

**Background:**
- White/Light gray for main content
- Subtle borders and shadows
- Professional financial dashboard aesthetic

### 2. Typography

**Font Hierarchy:**
- Headers: Bold, larger size
- Metrics: Medium weight, emphasis on numbers
- Body text: Regular weight, good line height
- Code/Technical: Monospace font

### 3. Layout Principles

**Structure:**
- Sidebar for controls (25% width)
- Main content area (75% width)
- Two-column layout for metrics vs charts
- Mobile-responsive breakpoints

**Spacing:**
- Consistent padding and margins
- Clear visual hierarchy
- Adequate white space
- Logical grouping of related elements

## Error Handling & Resilience

### 1. Error Categories

**User Input Errors:**
- Invalid symbols → Suggestions provided
- Invalid periods → Clear validation messages
- Empty inputs → Helpful placeholders

**Data Errors:**
- API failures → Cached data fallback
- Network timeouts → Retry suggestions
- Insufficient data → Alternative period suggestions

**System Errors:**
- Backend failures → Graceful degradation
- Cache corruption → Automatic cleanup
- Memory issues → Data size warnings

### 2. Fallback Strategies

**Progressive Degradation:**
- Show cached data when live data fails
- Display basic charts when advanced features fail
- Provide static commentary when AI fails

**User Guidance:**
- Clear error messages with next steps
- Popular symbol suggestions
- Help text and tooltips

## Integration with Backend

### 1. API Integration

**Clean Interface:**
```python
# Simple integration pattern
dashboard = StockDashboard()
analysis = dashboard.get_stock_analysis(symbol, period, language)

# All caching, error handling, and API coordination 
# is handled by the backend
```

**Error Propagation:**
- Backend exceptions caught and classified
- User-friendly error translation
- Automatic retry for transient failures

### 2. Data Flow

**Request Flow:**
1. User selects symbol/period in sidebar
2. Frontend validates input format
3. Backend fetches/calculates data (with caching)
4. Frontend renders charts and displays
5. Error boundaries catch and handle failures

**State Management:**
- Session state for UI preferences
- Backend manages data caching
- Clear separation of concerns

## Mobile Responsiveness

### 1. Layout Adaptations

**Mobile Layout:**
- Single column layout
- Collapsible sidebar
- Larger touch targets
- Simplified charts

**Tablet Layout:**
- Reduced sidebar width
- Stacked metrics
- Optimized chart sizes

### 2. Touch Interactions

**Chart Interactions:**
- Touch-friendly zoom controls
- Swipe for time navigation
- Tap for data points

## Future Expansion Framework

### 1. Easy Additions

**Component Extensions:**
- New chart types → Add to `charts.py`
- Additional metrics → Extend `metrics.py`
- New indicators → Add to display components

**Feature Toggles:**
- User preferences for advanced features
- A/B testing capabilities
- Progressive feature rollout

### 2. Medium Complexity Additions

**Enhanced Interactivity:**
- Real-time data updates
- Custom indicator selection
- Portfolio tracking
- Alert notifications

**Advanced Analytics:**
- Multiple symbol comparison
- Correlation analysis
- Backtesting visualization
- Sentiment analysis display

### 3. Advanced Features

**Multi-Page Application:**
- Portfolio management page
- Watchlist functionality
- Settings and preferences page
- Historical analysis tools

**Collaboration Features:**
- Shared dashboards
- Comments and annotations
- Export and reporting
- Social trading features

## Implementation Timeline

### Phase 1: Core MVP (Day 1)
- [ ] Basic app structure and layout
- [ ] Sidebar controls implementation
- [ ] Main price chart with indicators
- [ ] Basic metrics display
- [ ] AI commentary integration
- [ ] Error handling framework

### Phase 2: Polish & Performance (Day 2)
- [ ] Professional styling and colors
- [ ] Performance optimization
- [ ] Mobile responsiveness
- [ ] Advanced error handling
- [ ] User experience improvements
- [ ] Testing and debugging

### Phase 3: Enhancement (Future)
- [ ] Additional chart types
- [ ] More technical indicators
- [ ] Advanced user preferences
- [ ] Real-time features
- [ ] Export capabilities

## Dependencies

```txt
# Core Streamlit
streamlit>=1.28.0

# Visualization
plotly>=5.15.0

# Data manipulation (already included via backend)
pandas>=2.0.0

# Backend integration
# (src modules from backend MVP)
```

## Configuration

### UI Configuration (`config/ui_config.py`)

```python
# Chart configuration
CHART_CONFIG = {
    'height': 600,
    'template': 'plotly_white',
    'showlegend': True,
    'responsive': True
}

# Color scheme
COLORS = {
    'primary': '#1f77b4',
    'success': '#2ca02c', 
    'danger': '#d62728',
    'warning': '#ff7f0e',
    'neutral': '#7f7f7f'
}

# Layout configuration
LAYOUT = {
    'sidebar_width': 300,
    'main_columns': [2, 1],  # Chart:Metrics ratio
    'metrics_columns': 3,
    'mobile_breakpoint': 768
}

# Performance settings
PERFORMANCE = {
    'cache_ttl': 300,  # 5 minutes
    'max_data_points': 1000,
    'lazy_load_threshold': 500
}
```

## Testing Strategy

### 1. Component Testing

**UI Component Tests:**
- Sidebar control functionality
- Chart rendering with mock data
- Error state display
- Responsive layout behavior

### 2. Integration Testing

**Frontend-Backend Integration:**
- Data flow from backend to UI
- Error propagation and handling
- Session state management
- Cache behavior validation

### 3. User Experience Testing

**Usability Testing:**
- Symbol search and selection
- Chart interaction and navigation
- Mobile device compatibility
- Error recovery workflows

## Key Success Metrics

### 1. Performance Metrics
- Page load time < 2 seconds
- Chart rendering < 1 second
- Error recovery < 3 seconds
- Memory usage < 100MB

### 2. User Experience Metrics
- Symbol validation success rate > 95%
- Error rate < 5%
- User task completion rate > 90%
- Mobile usability score > 8/10

### 3. Code Quality Metrics
- Component reusability > 80%
- Code coverage > 90%
- Maintainability index > 7/10
- Performance benchmark compliance

## Summary

This frontend MVP design provides:

✅ **Professional UI** - Clean, modern financial dashboard design  
✅ **High Performance** - Multi-level caching and optimization  
✅ **Seamless Integration** - Clean coordination with backend MVP  
✅ **User-Friendly** - Intuitive controls and helpful error handling  
✅ **Extensible Architecture** - Clear paths for future enhancements  
✅ **Mobile Ready** - Responsive design for all devices  
✅ **Robust Error Handling** - Graceful degradation and recovery  

The design balances simplicity with functionality, ensuring a smooth development process while creating a professional tool that meets all assignment requirements and provides an excellent foundation for future growth.
