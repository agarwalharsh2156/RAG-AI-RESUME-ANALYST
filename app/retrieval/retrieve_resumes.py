from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from dotenv import load_dotenv
from collections import defaultdict
from config import PINECONE_INDEX_NAME, HYBIRD_ALPHA
from ingestion.sparse import load_vectorizer, get_sparse_vector
import os
 
load_dotenv()
 
# Load the exact same model you used during ingestion
model = SentenceTransformer("./768_d_model")
# model.save("./768_d_model")
vectorizer = load_vectorizer()

def _scale_vectors(dense_vector, sparse_vector, alpha):
    """
    Manually blend dense and sparse vectors using alpha.
 
    Why manual scaling instead of Pinecone's built-in alpha param:
    Pinecone's alpha only works correctly on indexes with vector_type='sparse'.
    Our index is vector_type='dense' (dotproduct), so Pinecone silently ignores
    the alpha param and returns pure dense results every time.
 
    The math:
    - Dense vectors are L2-normalized (magnitude = 1.0, values ~ -1 to 1)
    - TF-IDF sparse values are raw weights (values ~ 0.1 to 0.8, much smaller)
    - If we scale both by alpha directly, sparse is too weak to influence scores
    - So we first normalize sparse values to unit magnitude, then scale by (1-alpha)
 
    Result: dotproduct = (alpha * dense_score) + ((1-alpha) * sparse_score)
    Both components now on the same scale before blending.
    """
    # Scale dense side
    scaled_dense = [v * alpha for v in dense_vector]
 
    # Normalize sparse values to unit magnitude, then scale by (1 - alpha)
    sparse_values = sparse_vector["values"]
    if sparse_values:
        magnitude = sum(v * v for v in sparse_values) ** 0.5
        if magnitude > 0:
            normalized_sparse_values = [v / magnitude * (1 - alpha) for v in sparse_values]
        else:
            normalized_sparse_values = sparse_values
    else:
        normalized_sparse_values = []
 
    scaled_sparse = {
        "indices": sparse_vector["indices"],
        "values": normalized_sparse_values
    }
 
    return scaled_dense, scaled_sparse

def get_top_resumes(jd_text, top_k_chunks = 15, top_n_resumes= 5, alpha = HYBIRD_ALPHA):
    """
    Hybrid search version of get_top_resumes.
 
    alpha controls the dense vs sparse blend:
        1.0 = pure dense (semantic only)  — like your old version
        0.7 = 70% dense + 30% sparse      — good default for resumes
        0.5 = equal blend
        0.0 = pure sparse (keyword only)
 
    Everything else (scoring, ranking, output format) is identical to before.
    """
    pc = Pinecone(api_key=os.getenv("PINECONE_AI_RESUME_ANALYST_KEY"), ssl_verify = False)
    index = pc.Index(PINECONE_INDEX_NAME)
 
    # 1. Embed the JD - both dense and sparse
    dense_vector = model.encode(jd_text, normalize_embeddings=True).tolist()
    sparse_vector = get_sparse_vector(jd_text, vectorizer)

    # 2. Scale vectors manually (Pinecone's alpha param is unreliable for dense indexes)
    scaled_dense, scaled_sparse = _scale_vectors(dense_vector, sparse_vector, alpha)
 
    # 3. Hybird query to Pinecone
    response = index.query(
        vector=scaled_dense,
        sparse_vector=scaled_sparse,
        top_k=top_k_chunks,
        alpha = alpha,
        include_metadata=True,
        include_values=False
    )
 
    # 4. Group chunks by resume filename
    resume_groups = defaultdict(list)
    for match in response.matches:
        meta = match.metadata
        filename = meta.get("filename")
        resume_groups[filename].append({
            "score": match["score"],           # similarity from Pinecone (0 to 1)
            "section": meta.get("section", ""),
            "text": meta.get("text", "")[:800]
        })
 
    # 5. Calculate overall score per resume + rank them
    ranked_resumes = []
    for filename, chunks in resume_groups.items():
        if not chunks:
            continue
 
        avg_score = sum(chunk["score"] for chunk in chunks) / len(chunks)
        matched_count = len(chunks)
 
        # Bonus for important sections (you can tune these weights)
        important_sections = {"skills", "experience", "projects", "summary", "professional"}

        # bonus = sum(2.5 for chunk in chunks if chunk["section"].lower() in important_sections)
        # # Final overall score (0-100 scale)
        # overall_score = (avg_score * 75) + (matched_count * 2.0) + bonus

        bonus = sum(1.0 for chunk in chunks if chunk["section"].lower() in important_sections )
        base_score = avg_score * 100
        chunk_bonus = min(matched_count, 5) * 2

        overall_score = (base_score * 0.9) + chunk_bonus + bonus
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

