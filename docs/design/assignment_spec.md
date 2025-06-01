# Assignment Specification

## 1. Task Description
You are to develop a simple prototype of a financial dashboard in Streamlit that:

* Fetches historical stock price data (e.g., via a public API or a CSV file).
* Processes and visualizes data using Pandas (or equivalent).
* Integrates with the OpenAI API to generate a short, automated "market commentary" based on price development.

The purpose is to test your Python skills from the first year (variables, data structures, functions, classes, error handling), your ability to quickly learn new tools (Streamlit, OpenAI library), and your curiosity and creativity.

⏱ **Timeframe:** Max 1 day (8 hours)

## 2. Technical Specification

### Data
Use an open API (e.g., [Yahoo Finance via yfinance package] or Alpha Vantage) or a provided CSV file with at least 6 months of daily closing prices for one or more stocks.

### Backend (Python)
* Load data with Pandas.
* Calculate at least two simple technical indicators (e.g., moving average, standard deviation).
* Write clean functions/classes for data loading and calculations.

### Frontend (Streamlit)
* Display an interactive chart of price development + indicators.
* Allow the user to select time intervals and indicators via a sidebar.

### AI Integration (OpenAI)
* Call OpenAI's Chat Completion endpoint to generate a short (3–5 sentences) market commentary in Swedish or English, based on the calculated information (e.g., "Over the last 30 days, the X stock has risen by Y%; RSI is at Z, which indicates...").
* Display the AI-generated text in the app.

## 3. Extra Elements to Measure Motivation & Curiosity

*   **Improvement Suggestions:** Describe (in a short README) at least two ideas on how you would further develop the dashboard if you had more time (e.g., adding sentiment analysis, backtesting, notifications for large price movements).
*   **Reflection:** Write a few sentences about what you found most challenging, what you learned, and which parts of the code you are particularly satisfied with.

## 4. Deliverables

*   Code in a GitHub repo (or zip) with:
    *   `app.py` (Streamlit app)
    *   `requirements.txt`
    *   `README.md` with instructions for running (incl. API key for OpenAI if you have one).
*   Oral presentation (10–15 minutes) where you:
    *   Demonstrate the app and go through your code structure.
    *   Explain how the AI integration works and what the prompt does.
    *   Present your ideas for further development and reflect on what you learned.

## 5. Assessment Criteria

| Category                  | Weighting | What we look at                                   |
| :------------------------ | :-------- | :------------------------------------------------ |
| Code Quality              | 30 %      | Readability, modular structure, error handling    |
| Technical Functionality   | 30 %      | Data handling, calculations, interactivity        |
| AI Integration            | 20 %      | Prompt design, correct API call, relevance        |
| Presentation & Reflection | 10 %      | Clarity, maturity in reflection, creativity       |
| Motivation & Curiosity    | 10 %      | Improvement suggestions, willingness to learn more |
