import streamlit as st
import requests
import os
import json
# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Resume Analyst", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Mono', monospace;
    }

    .stApp {
        background-color: #0d0d0f;
        color: #e8e4dc;
    }

    /* Title */
    .main-title {
        font-family: 'Syne', sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #f0ebe1;
        margin-bottom: 0.2rem;
    }
    .main-sub {
        font-family: 'DM Mono', monospace;
        font-size: 0.75rem;
        color: #5a5a6a;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }

    /* Tab bar */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid #1f1f2e;
        background: transparent;
        padding: 0;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'DM Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #4a4a5a;
        padding: 0.75rem 1.5rem;
        border: none;
        background: transparent;
        border-bottom: 2px solid transparent;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        color: #c8f060 !important;
        border-bottom: 2px solid #c8f060 !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #e8e4dc !important;
        background: #141418 !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 2rem;
    }

    /* Section label */
    .section-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #5a5a6a;
        margin-bottom: 0.5rem;
    }

    /* Cards / containers */
    .info-card {
        background: #111115;
        border: 1px solid #1f1f2e;
        border-radius: 6px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
    }

    /* Status badge */
    .status-badge {
        display: inline-block;
        font-family: 'DM Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 0.25rem 0.7rem;
        border-radius: 3px;
    }
    .status-ready {
        background: #1a2e0d;
        color: #c8f060;
        border: 1px solid #3a5a1a;
    }
    .status-idle {
        background: #1a1a22;
        color: #5a5a6a;
        border: 1px solid #2a2a3a;
    }
    .status-processing {
        background: #2a1e0d;
        color: #f0a030;
        border: 1px solid #5a3a10;
    }

    /* Inputs */
    .stTextArea textarea, .stTextInput input {
        background: #111115 !important;
        border: 1px solid #1f1f2e !important;
        border-radius: 4px !important;
        color: #e8e4dc !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 0.82rem !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #c8f060 !important;
        box-shadow: 0 0 0 1px #c8f060 !important;
    }

    /* Buttons */
    .stButton > button {
        font-family: 'DM Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        background: #c8f060;
        color: #0d0d0f;
        border: none;
        border-radius: 3px;
        padding: 0.55rem 1.4rem;
        font-weight: 500;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        background: #d8ff70;
        transform: translateY(-1px);
    }
    .stButton > button:disabled {
        background: #1f1f2e !important;
        color: #3a3a4a !important;
        cursor: not-allowed !important;
        transform: none !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #111115;
        border: 1px dashed #2a2a3a;
        border-radius: 6px;
        padding: 0.5rem;
    }

    /* Analysis output */
    .analysis-output {
        background: #080809;
        border: 1px solid #1f1f2e;
        border-radius: 6px;
        padding: 1.4rem;
        min-height: 200px;
        font-family: 'DM Mono', monospace;
        font-size: 0.82rem;
        line-height: 1.7;
        color: #c8c4bc;
    }

    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #1a1a22;
        margin: 1.5rem 0;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background: #111115 !important;
        border: 1px solid #1f1f2e !important;
        color: #e8e4dc !important;
        font-family: 'DM Mono', monospace !important;
    }

    /* Number input */
    .stNumberInput input {
        background: #111115 !important;
        border: 1px solid #1f1f2e !important;
        color: #e8e4dc !important;
        font-family: 'DM Mono', monospace !important;
    }

    /* Multiselect */
    .stMultiSelect > div > div {
        background: #111115 !important;
        border: 1px solid #1f1f2e !important;
        color: #e8e4dc !important;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "ingestion_running" not in st.session_state:
    st.session_state.ingestion_running = False
if "ingestion_done" not in st.session_state:
    st.session_state.ingestion_done = False
if "generated_jd" not in st.session_state:
    st.session_state.generated_jd = ""


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">Resume Analyst</div>', unsafe_allow_html=True)
st.markdown('<div class="main-sub">AI-powered candidate screening system</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
LM_STUDIO_MODEL = "llama3.2-2b"


def stream_llm_response(system_prompt: str, user_prompt: str, placeholder):
    """Streams LLM response into a Streamlit placeholder. Returns full text."""
    payload = {
        "model": LM_STUDIO_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        "stream": True
    }
    full_text = ""
    try:
        with requests.post(LM_STUDIO_URL, json=payload, stream=True) as response:
            if response.status_code != 200:
                st.error(f"Server Error {response.status_code}: {response.text}")
                return ""
            for line in response.iter_lines():
                if not line:
                    continue
                decoded = line.decode("utf-8")
                if not decoded.startswith("data: "):
                    continue
                json_str = decoded[6:]
                if json_str.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(json_str)
                    if chunk.get("choices"):
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        full_text += content
                        placeholder.markdown(full_text + "▌")
                except json.JSONDecodeError:
                    continue
        placeholder.markdown(full_text)
        return full_text
    except requests.exceptions.RequestException as e:
        st.error(f"Connection failed: {e}")
        return ""


# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_ingestion, tab_jd, tab_analysis = st.tabs([
    "01 · Ingestion",
    "02 · Job Description",
    "03 · Analysis",
])

from config import RESUME_DIR, LLM_INSTRUCTIONS
from retrieval.retrieve_resumes import get_top_resumes
from retrieval.format_context import eng_prompt
from ingestion.ingest import upsert_to_index

# ══════════════════════════════════════════════
# TAB 1 — INGESTION
# ══════════════════════════════════════════════
with tab_ingestion:

    # Status row
    col_status, _ = st.columns([1, 3])
    with col_status:
        if st.session_state.ingestion_running:
            st.markdown('<span class="status-badge status-processing">● Processing</span>', unsafe_allow_html=True)
        elif st.session_state.ingestion_done:
            st.markdown('<span class="status-badge status-ready">✓ Index Ready</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge status-idle">○ Awaiting Upload</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Upload Resumes</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        label="Drop PDF resumes here or click to browse",
        type=["pdf"],
        accept_multiple_files=True,
        disabled=st.session_state.ingestion_running,
    )

    if uploaded_files:
        st.markdown(
            f'<div class="info-card"><span style="color:#c8f060;font-size:0.8rem;">'
            f'{len(uploaded_files)} file(s) selected</span><br>'
            + "<br>".join(
                f'<span style="color:#5a5a6a;font-size:0.72rem;">→ {f.name}</span>'
                for f in uploaded_files
            )
            + "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    ingest_btn = st.button(
        "Save & Index Resumes",
        disabled=not uploaded_files or st.session_state.ingestion_running,
        key="ingest_btn",
    )

    if ingest_btn and uploaded_files:
        st.session_state.ingestion_running = True
        st.session_state.ingestion_done = False
        st.rerun()

    # The actual ingestion runs on the rerun where ingestion_running=True
    if st.session_state.ingestion_running:
        with st.spinner("Saving and building vector index…"):
            try:
                for file in uploaded_files or []:
                    file_path = os.path.join(RESUME_DIR, file.name)
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                upsert_to_index(RESUME_DIR)
                st.session_state.ingestion_done = True
                st.success("Resumes indexed successfully. You may now use the other tabs.")
            except Exception as e:
                st.error(f"Ingestion failed: {e}")
            finally:
                st.session_state.ingestion_running = False
                st.rerun()


# ══════════════════════════════════════════════
# TAB 2 — JOB DESCRIPTION GENERATOR
# ══════════════════════════════════════════════
with tab_jd:

    tabs_disabled = st.session_state.ingestion_running

    if tabs_disabled:
        st.warning("Ingestion is in progress. Please wait until indexing is complete.")
    else:
        st.markdown('<div class="section-label">Role Details</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            jd_title = st.text_input("Job Title", placeholder="e.g. Senior Full Stack Engineer")
            jd_dept  = st.text_input("Department", placeholder="e.g. Engineering")
            jd_location = st.text_input("Location / Remote Policy", placeholder="e.g. Remote · US only")
        with col2:
            jd_exp = st.selectbox(
                "Experience Level",
                ["Intern", "Junior (0–2 yrs)", "Mid (2–5 yrs)", "Senior (5–8 yrs)", "Staff / Lead (8+ yrs)"]
            )
            jd_type = st.selectbox("Employment Type", ["Full-time", "Part-time", "Contract", "Freelance"])
            jd_salary = st.text_input("Salary Range (optional)", placeholder="e.g. INR 120k – INR 150k")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Responsibilities & Requirements</div>', unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        with col3:
            jd_responsibilities = st.text_area(
                "Key Responsibilities",
                placeholder="• Build and maintain REST APIs\n• Collaborate with design team\n• Own deployment pipelines",
                height=140,
            )
        with col4:
            jd_requirements = st.text_area(
                "Must-Have Skills / Requirements",
                placeholder="• React, Node.js, PostgreSQL\n• 4+ years professional experience\n• Strong system design fundamentals",
                height=140,
            )

        jd_nice_to_have = st.text_area(
            "Nice-to-Have (optional)",
            placeholder="• Experience with Kubernetes\n• Open-source contributions",
            height=80,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        gen_btn = st.button("Generate Job Description", key="gen_jd_btn")

        if gen_btn:
            user_prompt = f"""
Generate a professional job description using the following details:

Title: {jd_title}
Department: {jd_dept}
Location: {jd_location}
Experience Level: {jd_exp}
Employment Type: {jd_type}
Salary Range: {jd_salary or 'Not specified'}

Key Responsibilities:
{jd_responsibilities}

Must-Have Skills/Requirements:
{jd_requirements}

Nice-to-Have:
{jd_nice_to_have or 'None specified'}

Write a compelling, structured job description with sections: About the Role, Responsibilities, Requirements, Nice to Have, and What We Offer. Use a professional but engaging tone. Keep the entire Job Description within 10-15 lines.
            """.strip()

            system_prompt = "You are an expert HR writer. Write clear, structured, and compelling job descriptions."

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">Generated Description</div>', unsafe_allow_html=True)
            placeholder = st.empty()

            with st.spinner("Generating…"):
                result = stream_llm_response(system_prompt, user_prompt, placeholder)

            if result:
                st.session_state.generated_jd = result
                st.success("Job description saved — available in the Analysis tab.")


# ══════════════════════════════════════════════
# TAB 3 — FINAL ANALYSIS
# ══════════════════════════════════════════════
with tab_analysis:

    tabs_disabled = st.session_state.ingestion_running

    if tabs_disabled:
        st.warning("Ingestion is in progress. Please wait until indexing is complete.")
    else:
        st.markdown('<div class="section-label">Job Description</div>', unsafe_allow_html=True)

        # Pre-fill from JD generator if available
        if st.session_state.generated_jd:
            st.markdown(
                '<span class="status-badge status-ready" style="margin-bottom:0.6rem;display:inline-block;">'
                '✓ Auto-filled from generator</span>',
                unsafe_allow_html=True,
            )

        query = st.text_area(
            label="Paste or edit the job description / hiring query below",
            value=st.session_state.generated_jd if st.session_state.generated_jd else "",
            placeholder="e.g. I want to hire a Senior Full Stack Developer with React and Node.js experience…",
            height=180,
        )

        col_k1, col_k2 = st.columns(2)
        with col_k1:
            top_k_chunks = st.number_input("Top K chunks to retrieve", min_value=1, max_value=50, value=15)
        with col_k2:
            top_n_resumes = st.number_input("Top N resumes to surface", min_value=1, max_value=20, value=5)

        st.markdown("<br>", unsafe_allow_html=True)

        analyze_btn = st.button(
            "Run Analysis",
            disabled=not query.strip(),
            key="analyze_btn",
        )

        if analyze_btn and query.strip():
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">AI Analysis</div>', unsafe_allow_html=True)

            with st.spinner("Retrieving top resumes…"):
                ranked_resumes = get_top_resumes(
                    query,
                    top_k_chunks=int(top_k_chunks),
                    top_n_resumes=int(top_n_resumes),
                )
                final_prompt = eng_prompt(ranked_resumes, query)

            placeholder = st.empty()
            stream_llm_response(LLM_INSTRUCTIONS, final_prompt, placeholder)