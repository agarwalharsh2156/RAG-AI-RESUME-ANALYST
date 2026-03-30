import streamlit as st
from google import genai
from google.genai import types
from config import LLM_MODEL, LLM_INSTRUCTIONS, RESUME_DIR
from retrieval.retrieve_resumes import get_top_resumes
from retrieval.format_context import eng_prompt
from ingestion.ingest import upsert_to_index
import os

# 1. Basic Page Config
st.set_page_config(page_title="Resume Analyst", layout="centered")
st.title("📄 AI Resume Analyst")

uploaded_files = st.file_uploader(
    "Upload resumes in pdf format:", 
    type=["pdf"],
    accept_multiple_files= True
)

def save_and_upsert(upload):
    for file in uploaded_files:
        file_path = os.path.join(RESUME_DIR, file.name)
        with open (file_path, "wb") as f:
            f.write(file.getbuffer())
    upsert_to_index(RESUME_DIR)


if uploaded_files:
    save_and_upsert(upload=uploaded_files)

# 2. Minimal Input Section
query = st.text_area("Hiring Query:", "I want to hire a Full Stack Web Developer")

if st.button("Analyze Resumes"):
    with st.spinner("Fetching the best resumes out."):
        # getting top resumes out based on the query
        ranked_resumes = get_top_resumes(query, top_k_chunks = 15, top_n_resumes = 5)

        # getting the augmented prompt with resume context and the query
        final_prompt = eng_prompt(ranked_resumes, query)

        client = genai.Client()

        # querying the model to get it's analysis for the given resumes
        response = client.models.generate_content_stream(
            model = LLM_MODEL,
            config = types.GenerateContentConfig(
                system_instruction = LLM_INSTRUCTIONS
            ),
            contents= final_prompt
        )

        # 3. Streaming to UI
        st.subheader("Analysis")
        container = st.container(height= 500)
        placeholder = container.empty()
        full_text = ""
        
        for chunk in response:
            full_text += chunk.text
            # Update the UI in real-time
            placeholder.markdown(full_text)