from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent.parent

PINECONE_INDEX_NAME = "hybrid-resume-index"
PINECONE_INDEX_CLOUD = "aws"
PINECONE_INDEX_REGION = "us-east-1"
DENSE_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
# DENSE_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
PINECONE_INDEX_DIMENSION = 768 if DENSE_MODEL_NAME == "sentence-transformers/all-mpnet-base-v2" else 384
PINECONE_INDEX_METRIC = "cosine"
PINECONE_VECTOR_TYPE = "dense"


LLM_MODEL = 'gemini-2.5-flash'
DEFAULT_TOP_K = 1
DEFAULT_NAMESPACE = "ai-labs-batch-2026"
RESUME_DIR = os.path.join(BASE_DIR, 'resumes')
LLM_INSTRUCTIONS = """
Role: Act as an Expert Resume Analyst and Technical Recruiter with 15+ years of experience in talent acquisition.
Objective: Critically evaluate the provided resume against a specific job description (or general industry standards) to identify strengths, gaps, and optimization opportunities.
Responsibilities:
Keyword Analysis: Identify missing technical and soft skills.
Impact Assessment: Evaluate if experience is described using quantifiable achievements (e.g., "Increased revenue by 20%") rather than just tasks.
Formatting Check: Note any issues with readability or ATS (Applicant Tracking System) compatibility.
Actionable Advice: Provide specific bullet-point suggestions for improvement.
Output Structure:
You must return your analysis strictly in the following JSON format:
json
{
  "resume_id": file_name,
  "resume_score": "0-100",
  "executive_summary": "Short overview of candidate fit",
  "strengths": ["list", "of", "key", "wins"],
  "critical_gaps": ["missing", "skills", "or", "experiences"],
  "ats_optimization": {
    "formatting_issues": "string",
    "suggested_keywords": ["keyword1", "keyword2"]
  },
  {
    //same format as above.
  }
}"""
