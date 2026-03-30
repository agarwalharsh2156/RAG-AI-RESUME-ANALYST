from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from dotenv import load_dotenv
from collections import defaultdict
from config import PINECONE_INDEX_NAME, DENSE_MODEL_NAME
import os
 
load_dotenv()
 
# Load the exact same model you used during ingestion
model = SentenceTransformer("./768_d_model")
# model.save("./768_d_model")
def get_top_resumes(jd_text, top_k_chunks = 15, top_n_resumes= 5):
    """
    Main function you will call.
    Returns top N resumes ranked by overall match score.
    """
    pc = Pinecone(api_key=os.getenv("PINECONE_AI_RESUME_ANALYST_KEY"), ssl_verify = False)
    index = pc.Index(PINECONE_INDEX_NAME)
 
    # 1. Embed the Job Description
    query_vector = model.encode(jd_text, normalize_embeddings=True).tolist()
 
    # 2. Query Pinecone - get best matching chunks
    response = index.query(
        vector=query_vector,
        top_k=top_k_chunks,
        include_metadata=True,
        include_values=False
    )
 
    # 3. Group chunks by resume filename
    resume_groups = defaultdict(list)
    for match in response.matches:
        meta = match.metadata
        filename = meta.get("filename")
 
        resume_groups[filename].append({
            "score": match["score"],           # similarity from Pinecone (0 to 1)
            "section": meta.get("section", ""),
            "text": meta.get("text", "")[:800]
        })
 
    # 4. Calculate overall score per resume + rank them
    ranked_resumes = []
    for filename, chunks in resume_groups.items():
        if not chunks:
            continue
 
        avg_score = sum(chunk["score"] for chunk in chunks) / len(chunks)
        matched_count = len(chunks)
 
        # Bonus for important sections (you can tune these weights)
        important_sections = {"skills", "experience", "projects", "summary", "professional"}
        bonus = sum(2.5 for chunk in chunks if chunk["section"].lower() in important_sections)
 
        # Final overall score (0-100 scale)
        overall_score = (avg_score * 75) + (matched_count * 2.0) + bonus
        overall_score = min(100.0, round(overall_score, 1))
 
        ranked_resumes.append({
            "filename": filename,
            "overall_score": overall_score,
            "matched_chunks": matched_count,
            "top_sections": [c["section"] for c in chunks[:4]],
            "chunks": chunks   # full details if you want to show later
        })
 
    # 5. Sort and return top N
    ranked_resumes.sort(key=lambda x: x["overall_score"], reverse=True)
    return ranked_resumes[:top_n_resumes]

