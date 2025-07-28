# Casting

This app provides a small example of using the OpenAI Agents SDK with
Streamlit to analyse financial statements. Upload a file such as a CSV or
Excel spreadsheet and the app can compute simple *casting* totals (summing all
numeric columns). You can also query an OpenAI model about the contents of the
file.

## Setup

1. Copy `.env.example` to `.env` and set your `OPENAI_API_KEY`.
2. Install the required dependencies (for example with `pip install -r requirements.txt`).
3. Run the app with `streamlit run streamlit_app.py`.

