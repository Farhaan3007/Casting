import streamlit as st
import pandas as pd
from dotenv import load_dotenv
try:
    from openai import OpenAI
except Exception:  # pragma: no cover - fallback when openai isn't available
    OpenAI = None
from PyPDF2 import PdfReader
from docx import Document
from agents import Agent, Runner

# Load API key from .env
load_dotenv()

st.title("Agentic File Assistant (using Agents SDK)")

uploaded = st.file_uploader(
    "Upload a file (txt, csv, pdf, docx, xlsx)",
    type=["txt", "csv", "pdf", "docx", "xlsx"]
)

def extract_text(f):
    content = None
    if f.type == "text/plain":
        content = f.read().decode()
    elif f.type == "text/csv":
        content = f.read().decode()
    elif f.type == "application/pdf":
        pdf = PdfReader(f)
        content = "\n".join(p.extract_text() or "" for p in pdf.pages)
    elif f.type.endswith("wordprocessingml.document"):
        doc = Document(f)
        content = "\n".join(p.text for p in doc.paragraphs)
    elif f.type.endswith("sheet"):
        df = pd.read_excel(f)
        content = df.to_csv(index=False)
    return content

def load_dataframe(f):
    """Return a DataFrame if file is csv or excel."""
    df = None
    if f.type == "text/csv":
        f.seek(0)
        df = pd.read_csv(f)
    elif f.type.endswith("sheet"):
        f.seek(0)
        df = pd.read_excel(f)
    return df

def cast_financials(df: pd.DataFrame) -> pd.Series:
    """Simple casting: sum numeric columns."""
    if df is None:
        return pd.Series()
    numeric_df = df.select_dtypes(include="number")
    return numeric_df.sum()

if uploaded:
    text = extract_text(uploaded)
    df = load_dataframe(uploaded)
    if not text:
        st.warning("Could not extract text.")
    else:
        st.info("File uploaded successfully.")
        if df is not None and st.button("Compute Casting"):
            totals = cast_financials(df)
            st.subheader("Casting Totals")
            st.write(totals)

        if st.button("Analyze Financials"):
            fin_agent = Agent(
                name="Financial Extractor",
                instructions=(
                    "Extract the profit & loss statement, statement of financial "
                    "position, statement of changes in equity and cashflow "
                    "statement for both years. Respond in Markdown."
                ),
            )
            notes_agent = Agent(
                name="Notes Extractor",
                instructions="Extract the notes for both years. Respond in Markdown.",
            )
            compare_agent = Agent(
                name="Comparison Agent",
                instructions=(
                    "Compare the figures in the financial statements and the "
                    "notes and identify any discrepancies. Respond in Markdown."
                ),
            )
            summary_agent = Agent(
                name="Summary Agent",
                instructions=(
                    "Summarize the discrepancies in a concise Markdown table "
                    "with columns 'Item' and 'Issue'."
                ),
            )

            with st.spinner("Running Financial Extractor..."):
                fin_result = Runner.run_sync(fin_agent, input=text)
            with st.spinner("Running Notes Extractor..."):
                notes_result = Runner.run_sync(notes_agent, input=text)
            compare_input = f"STATEMENTS:\n{fin_result.final_output}\n\nNOTES:\n{notes_result.final_output}"
            with st.spinner("Running Comparison Agent..."):
                compare_result = Runner.run_sync(compare_agent, input=compare_input)
            with st.spinner("Running Summary Agent..."):
                summary_result = Runner.run_sync(summary_agent, input=compare_result.final_output)
            st.markdown("**Summary of Errors:**")
            st.write(summary_result.final_output)
