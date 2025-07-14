import json
import streamlit as st
from pypdf import PdfReader
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import re

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


def clean_and_parse_json(raw_text):
    cleaned = re.sub(r"```(?:json)?\s*", "", raw_text)
    cleaned = cleaned.replace("```", "").strip()
    
    return json.loads(cleaned)

def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text
def read_text_file(file):
    return file.read().decode("utf-8") if hasattr(file, 'read') else file
def getResumeAnalysis(resume_text, jd):
    prompt = PromptTemplate(
        input_variables=["resume", "jd"],
        template="""
            You are an expert resume evaluator. Given a resume and a job description, your task is to:
            1. Analyze the resume against the job description.
            2. Identify key strengths and weaknesses.
            3. Provide actionable feedback to improve the resume.
            Respond **professionally and directly** — do not narrate your steps, avoid saying "Let's analyze..." or similar. Just give the analysis. The analysis should be concise and actionable. Also tell if the resume is relevant to the job description or not.
            Your response should be in JSON format with the following structure:
            {{
            "relevance_score": "<score out of 10>",
            "missing_keywords": ["<keyword1>", "<keyword2>", "..."],
            "suggestions": ["<suggestion1>", "<suggestion2>", "..."]
            }}

            Only return valid JSON — no extra explanations.

            RESUME:
            {resume}

            JOB DESCRIPTION:
            {jd}

            """
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        api_key=api_key,
        temperature=0
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    op= chain.run(resume=resume_text, jd=jd)
    print("Output: - app.py:64", op)
    return op

# ------------------------ Streamlit UI ------------------------

st.set_page_config(page_title="Resume Analyzer", page_icon="📄")
st.title("📄 Analyze Your Resume")
st.caption("Scan. Analyze. Improve. Let AI help you land the job 🎯")


resume_file = st.file_uploader("Upload your Resume", type=["pdf"])

jd_file = st.file_uploader("Upload Job Description", type=["txt"])

# Centered Analyze button
analyze_clicked = False
if resume_file and jd_file:
    
    analyze_clicked = st.button("🚀 Analyze", type="primary")

# Run analysis after button click
if analyze_clicked:
    with st.spinner("📄 Analyzing files..."):
        resume_text = read_pdf(resume_file)
        jd_text = read_text_file(jd_file)
        result = getResumeAnalysis(resume_text, jd_text)

        try:
            parsed = clean_and_parse_json(result)
            st.markdown('<h3 style="text-align: center;">🧠 Analysis Result</h3>', unsafe_allow_html=True)
            st.divider()

            score = parsed.get("relevance_score", "N/A")
            st.markdown("### 📊 Relevance Score")
            if score != "N/A" and "/10" not in score:
                score = f"{score}/10"
            st.metric(label="", value=score)

            keywords = parsed.get("missing_keywords", [])
            if len(keywords)>0:
                st.markdown("### 🛠 Missing Keywords")
                tags_html = ''.join([
                    f'<span style="background-color:#e0f7fa; color:#00796b; padding:5px 10px; margin:5px; border-radius:10px; display:inline-block;">{kw}</span>'
                    for kw in keywords
                ])
                st.markdown(f'<div style="line-height: 2.5;">{tags_html}</div>', unsafe_allow_html=True)
            else:
                st.info("✅ No missing keywords found.")

            st.markdown("### 🛠 Suggestions to Improve the Resume")
            suggestions = parsed.get("suggestions", [])
            if suggestions:
                for s in suggestions:
                    st.markdown(f"- {s}")
            else:
                st.info("✅ No suggestions needed. Great resume!")

        except json.JSONDecodeError:
            st.warning("⚠️ Couldn't parse response as JSON. Showing raw output:")
            st.text_area("LLM Response", result, height=400)