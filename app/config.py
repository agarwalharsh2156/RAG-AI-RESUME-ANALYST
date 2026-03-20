from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent

PINECONE_INDEX_NAME = "hybrid-resume-index"
PINECONE_INDEX_CLOUD = "aws"
PINECONE_INDEX_REGION = "us-east-1"
PINECONE_INDEX_DIMENSION = 384
PINECONE_INDEX_METRIC = "dotproduct"

DENSE_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
LLM_MODEL = 'gemini-2.5-flash'
DEFAULT_TOP_K = 1
DEFAULT_NAMESPACE = "ai-labs-batch-2026"

RESUME_DIR = os.path.join(BASE_DIR, 'resumes')
