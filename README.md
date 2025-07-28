# Casting

This app provides a small example of using the OpenAI Agents SDK with
Streamlit to analyse financial statements. Upload a file such as a CSV or
Excel spreadsheet and the app can compute simple *casting* totals (summing all
numeric columns). It also demonstrates a pipeline of multiple agents that
extract statements and notes, compare the numbers and output a summary table
of any discrepancies.

## Setup

1. Copy `.env.example` to `.env` and set your `OPENAI_API_KEY`.
2. Install the required dependencies (for example with `pip install -r requirements.txt`).
3. Run the app with `streamlit run streamlit_app.py`.

When you press **Analyze Financials** in the web interface, the app runs four
agents in sequence: it extracts the statements, extracts the notes, compares
the figures and then produces a summary table of any issues found.

