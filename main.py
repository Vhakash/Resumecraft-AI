import streamlit as st
import PyPDF2
import io
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title = "AI Resume Critiquer", page_icon = "📝",  layout = "centered")

st.title("AI Resume Critiquer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

uploaded_file = st.file_uploader("Upload your resume(PDF or txt)", type = ["pdf", "txt"])
job_role = st.text_input("Enter the job role you're applying for:")

analyze = st.button("Analyze Resume")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text    
    

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

if(analyze and uploaded_file):
    st.write("Analyzing your resume...")
    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("File does not contain any text.")
            st.stop()

        prompt = f"""Please analyze this resume and provide constructive feedback.

        Focus on the following aspects:
        1. Content Clarity and Impact
        2. Skills presentation
        3. Experience descriptions
        4. Special improvements for {job_role if job_role else 'general job applications'}

        Resume content:
        {file_content}

        please provide your analysis in a clear, structured format with specific recommendations.
        """
        
        if not GOOGLE_API_KEY:
            st.error("Google API key not found. Please check your .env file.")
            st.stop()
            
        client = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            max_tokens=1000
        )
        
        # Format the prompt with system context
        full_prompt = f"""You are an expert resume reviewer with years of experience.

{prompt}"""
        
        response = client.invoke(full_prompt)
        st.markdown("### Analysis Results")
        st.markdown(response.content)
    except Exception as e:
        st.error(f"Error occurred: {str(e)}")