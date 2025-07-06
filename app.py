 
import time
import streamlit as st
from pypdf import PdfReader
apikey= st.secrets["API_KEY"]
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

st.title("📄 Analyze Your Resume 👋")
st.caption("Scan. Analyze. Improve. Let AI help you land the job 🎯")

file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
if file:
    with st.spinner("Analyzing your resume..."):
        
        resume_text = read_pdf(file)    
    