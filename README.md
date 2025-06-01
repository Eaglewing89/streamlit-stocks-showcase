# Streamlit Stocks Showcase

This project is a Streamlit-based financial dashboard that visualizes stock data, calculates technical indicators, and generates AI-powered market commentary.

## Running the Application

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd streamlit-stocks-showcase
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set up OpenAI API Key:**
    Ensure you have an OpenAI API key. You can set it as an environment variable:
    ```bash
    export OPENAI_API_KEY='your_api_key_here'
    ```
    Alternatively, the application will prompt you to enter it when it first runs.
4.  **Run the Streamlit app:**
    ```bash
    streamlit run streamlit/app.py
    ```

## Project Structure

*   `src/`: Contains the backend logic, including data fetching, technical analysis, and AI integration.
*   `streamlit/`: Contains the frontend Streamlit application code.
*   `tests/`: Contains unit and integration tests for the project.
*   `data/`: Stores cached data and logs.
*   `docs/`: Contains project documentation.

## Improvement Suggestions

1.  **Develop Backend into a Python Library:** Transform the backend into a standalone Python library. This library would offer advanced analysis for stocks, derivatives, and other tradable assets. It could then be integrated as a tool within larger AI agent systems designed for autonomous portfolio creation and management.
2.  **Enhance Portfolio Management Features:** Introduce capabilities for users to create and manage investment portfolios. This would include analytics such as risk estimation and performance tracking.
3.  **Prioritize Software Engineering Best Practices:** Before adding more frontend features, focus on ensuring the entire project adheres to the highest software engineering standards. This includes addressing any existing technical debt.
4.  **Expand Technical Indicators:** Incorporate a broader array of technical indicators and provide users with the ability to customize their parameters.
5.  **Comprehensive Testing Suite:** Continue to build out the `pytest` suite with reusable fixtures and factories to maintain high test coverage and ensure code reliability.

## Reflection

The project was a valuable learning experience in managing scope under time constraints. While completed on time, it was a close call, highlighting the need for more conservative planning. The robust testing suite for the backend provided significant confidence during development and pull request reviews. The backend itself is solid and designed for extensibility.

However, the initial design phase led to some technical debt, and the time allocated to frontend testing was insufficient due to the extensive features implemented in the backend. The reactive design of the frontend, while functional, was perhaps an unnecessary complexity for this prototype.

Key takeaways include the importance of meticulous time planning and scoping. Maintaining rigorous code review practices, even under pressure, is crucial, though the final few pull requests felt rushed. The most significant lesson is to better align project scope with available time to ensure all aspects, including frontend testing and documentation, receive adequate attention.
