import os
import asyncio
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader
from docx import Document
from agents import Agent, Runner

# Load API key from .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

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

if uploaded:
    text = extract_text(uploaded)
    if not text:
        st.warning("Could not extract text.")
    else:
        st.text_area("Preview", text[:2000], height=300)
        user_query = st.text_input("Ask your agent about this file:")

        if st.button("Run Agent") and user_query:
            agent = Agent(
                name="File Agent",
                instructions="Extract the document in markdown",
                model="gpt-4o",
            )
            prompt = f"{text[:4000]}\n\nUser question: {user_query}"
            result = asyncio.run(Runner.run(agent, input=prompt))
            st.markdown("**Agent Response:**")
            st.write(result.final_output)
