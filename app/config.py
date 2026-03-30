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
### ROLE
You are a Senior Technical Recruiter. Your task is to analyze a provided pool of candidates to determine their suitability for specific job roles based on the data provided below.

### CONSTRAINTS
1. ONLY use the information provided in the CANDIDATE POOL section.
2. Always refer to candidates by their unique ID.
3. If a candidate lacks a specific skill required for a role, state it clearly as a "Gap."
4. Provide objective, evidence-based reasoning for your analysis.

### CANDIDATE POOL
The following is the complete database of available resumes, including their pre-assigned overall scores and full text:


### INSTRUCTIONS
When the user provides a Job Description or asks for a comparison, evaluate the candidates from the pool above. Rank them based on their IDs and explain how their specific experience (Content) justifies their Overall Score.

List their strengths, weaknesses and potential improvement suggestions.
""".strip()

TEST_QUERY = """Act as a Junior Data Scientist with 6 months of internship experience.
Your technical stack includes Python (Pandas, Scikit-Learn), SQL, and Tensorflow, PyTorch.
You are helping a senior lead refine a predictive model for churn.
Answer questions with a focus on data cleaning and exploratory data analysis (EDA).
If a task involves machine learning, suggest using a Random Forest or Logistic Regression.
Keep explanations practical, mentioning specific libraries or functions like .groupby() or .fillna().
Do not suggest deep learning or complex neural networks unless specifically asked.
Maintain a professional, eager-to-learn, and collaborative tone.
Always mention the importance of checking for null values and outliers.
Limit your initial responses to 3 concise bullet points."""
