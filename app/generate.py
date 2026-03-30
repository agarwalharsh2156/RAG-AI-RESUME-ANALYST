import streamlit as st
# from google import genai
# from google.genai import types
from config import RESUME_DIR, LLM_INSTRUCTIONS
import requests
import os
import json

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

query = st.text_area("Hiring Query:", "I want to hire a Full Stack Web Developer")

from retrieval.retrieve_resumes import get_top_resumes
from retrieval.format_context import eng_prompt
from ingestion.ingest import upsert_to_index

if uploaded_files:
    save_and_upsert(upload=uploaded_files)


if st.button("Analyze Resumes"):
    # Change spinner to a container so it doesn't block the stream
    with st.spinner("Preparing analysis..."):
        ranked_resumes = get_top_resumes(query, top_k_chunks = 15, top_n_resumes = 3)
        final_prompt = eng_prompt(ranked_resumes, query)
        # final_prompt = "Analyze this: " + query # Dummy prompt for testing

        # 1. Setup API call with stream=True
        url = "http://localhost:1234/v1/chat/completions" 
    
        payload = {
            "model": "llama3.2-2b",
            "messages": [ 
                {"role": "system", "content": LLM_INSTRUCTIONS},
                {"role": "user", "content": final_prompt}
            ], 
            "stream": True
        }

        # 2. Streaming to UI
        st.subheader("Analysis")
        placeholder = st.empty()
        full_text = ""

        try:
            with requests.post(url, json=payload, stream=True) as response:
                # Check if the request itself failed (e.g., 404 or 500)
                if response.status_code != 200:
                    st.error(f"Server Error {response.status_code}: {response.text}")
                    st.stop()

                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        
                        # Skip "keep-alive" comments or empty lines
                        if not decoded_line.startswith("data: "):
                            continue
                            
                        # Remove "data: " prefix
                        json_str = decoded_line[6:] 

                        # Check for the stream end signal
                        if json_str.strip() == "[DONE]":
                            break

                        try:
                            chunk = json.loads(json_str)
                            
                            # Robustly extract content
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                
                                full_text += content
                                placeholder.markdown(full_text + "▌")
                                
                        except json.JSONDecodeError:
                            continue
                            
            # Final update to remove cursor
            placeholder.markdown(full_text)

        except requests.exceptions.RequestException as e:
            st.error(f"Connection failed: {e}")