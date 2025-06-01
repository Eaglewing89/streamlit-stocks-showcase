# Frontend Implementation

The frontend of the Streamlit Stocks Showcase is built using Streamlit, a Python library for creating interactive web applications for data science and machine learning projects.

## Core Components

Located in the `streamlit/` directory, the frontend is structured as follows:

*   **`app.py`**: This is the main entry point for the Streamlit application. It orchestrates the overall layout and anipd interaction flow of the dashboard.

*   **`components/`**: This directory contains reusable UI modules that make up the different parts of the dashboard.
    *   `charts.py`: Responsible for generating and displaying interactive charts of stock prices and technical indicators (e.g., using Plotly or Matplotlib).
    *   `display.py`: Contains functions for displaying various pieces of information, such as the AI-generated market commentary, stock metrics, and other textual or numerical data.
    *   `errors.py`: Handles the display of error messages or notifications to the user in a user-friendly way.
    *   `metrics.py`: (If applicable, otherwise remove or adjust) Specifically handles the display of key financial metrics or summary statistics.
    *   `sidebar.py`: Defines the content and interactivity of the sidebar, which typically includes user inputs like stock selection, date range pickers, and indicator choices.

*   **`config/`**: Contains configuration files specific to the UI.
    *   `ui_config.py`: Stores UI-related settings, such as chart color schemes, layout preferences, or default values for input fields.

*   **`utils/`**: Provides utility functions to support the frontend operations.
    *   `formatters.py`: Includes functions for formatting data for display (e.g., currency formatting, date formatting).
    *   `session.py`: Manages Streamlit session state, allowing the application to store and persist user inputs or application state across interactions.
    *   `validators.py`: Contains functions for validating user inputs from the sidebar or other interactive elements.

## User Interface and Interaction

*   **Sidebar for Controls**: Users interact with the dashboard primarily through a sidebar. Here, they can:
    *   Select the stock(s) to analyze.
    *   Choose the time interval for the historical data.
    *   Select which technical indicators to display on the chart.

*   **Main Display Area**: The central part of the dashboard displays:
    *   An interactive chart showing historical stock prices and the selected technical indicators.
    *   The AI-generated market commentary based on the current data and analysis.
    *   Other relevant metrics or data points.

## Data Flow

1.  User inputs from the `sidebar.py` are captured.
2.  These inputs are validated by `validators.py` and managed using `session.py`.
3.  `app.py` coordinates with the backend (via functions in `src/`) to fetch and process the required stock data and generate AI commentary based on the user's selections.
4.  The retrieved and processed data is then passed to the appropriate components in `streamlit/components/`:
    *   `charts.py` visualizes the stock data and indicators.
    *   `display.py` shows the AI commentary and other textual/numerical information.
5.  Error messages, if any, are handled and displayed by `errors.py`.

Streamlit's reactive nature ensures that the dashboard updates automatically whenever user inputs change, providing a seamless and interactive experience.
