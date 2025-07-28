import os
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
openai_api_key = os.getenv("OPENAI_API_KEY")
if OpenAI:
    client = OpenAI(api_key=openai_api_key)
else:
    client = None

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
        st.text_area("Preview", text[:2000], height=300)
        if df is not None and st.button("Compute Casting"):
            totals = cast_financials(df)
            st.subheader("Casting Totals")
            st.write(totals)

        user_query = st.text_input("Ask your agent about this file:")

        if st.button("Run Agent") and user_query:
            instructions = "Analyze the financial statement and provide findings in markdown."
            agent = Agent(name="File Agent", instructions=instructions, model="gpt-4o")
            prompt = f"{text[:4000]}\n\nUser question: {user_query}"
            result = Runner.run_sync(agent, input=prompt)
            st.markdown("**Agent Response:**")
            st.write(result.final_output)
