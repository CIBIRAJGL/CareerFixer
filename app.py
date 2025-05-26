import streamlit as st
import PyPDF2
import io
import requests
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="AI Resume Critiquer", page_icon="📃", layout="centered")

st.title("AI Resume Critiquer")
st.markdown("Upload your resume and get AI-powered feedback!")

# Hugging Face Settings
HF_API_KEY = os.getenv("HF_API_KEY")
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
job_role = st.text_input("Enter the job role you're targeting (optional)")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    return "\n".join([page.extract_text() for page in pdf_reader.pages])

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

if st.button("Analyze Resume") and uploaded_file:
    try:
        with st.spinner("Analyzing resume..."):
            file_content = extract_text_from_file(uploaded_file)
            
            if not file_content.strip():
                st.error("File content is empty")
                st.stop()

            prompt = f"""Analyze this resume and provide structured feedback:
            1. Content clarity and impact
            2. Skills presentation
            3. Experience descriptions
            4. {"Improvements for " + job_role if job_role else "General improvements"}
            
            Resume content:
            {file_content[:3000]}  # Limit input length
            
            Provide concise recommendations in bullet points."""

            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 1000,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(API_URL, headers=HEADERS, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    analysis = result[0].get('generated_text', 'No analysis generated')
                    st.markdown("### Analysis Results")
                    st.markdown(analysis)
                else:
                    st.error("Unexpected response format from API")
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
