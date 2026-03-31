# """
# test_hybrid.py

# Run this after ingestion to verify hybrid search is working correctly.
# Compares results across three alpha values so you can see how ranking shifts.

# Usage (from the app/ folder):
#     python test_hybrid.py
# """

# from retrieval.retrieve_resumes import get_top_resumes
# from retrieval.format_context import eng_prompt

# JD = "Need a backend engineer with strong experience in FastAPI, Celery, Redis, Kafka, Terraform, Kubernetes, PostgreSQL and Docker."


# def run_test(label, alpha):
#     print(f"\n{'=' * 60}")
#     print(f"TEST: {label}  (alpha={alpha})")
#     print('=' * 60)
#     results = get_top_resumes(JD, top_k_chunks=15, top_n_resumes=5, alpha=alpha)
#     if not results:
#         print("  No results returned — check ingestion and index.")
#         return results
#     for i, r in enumerate(results, 1):
#         print(f"  {i}. {r['filename']:<40}  score: {r['overall_score']}  chunks: {r['matched_chunks']}")
#     return results


# if __name__ == "__main__":
#     hybrid_results  = run_test("Hybrid — default",       alpha=0.7)
#     dense_results   = run_test("Pure Dense (old mode)",  alpha=1.0)
#     keyword_results = run_test("Keyword-heavy",          alpha=0.3)

#     # Show the formatted context that gets sent to the LLM
#     if hybrid_results:
#         print(f"\n{'=' * 60}")
#         print("FORMATTED CONTEXT SENT TO LLM (hybrid top-3, first 2000 chars)")
#         print('=' * 60)
#         context = eng_prompt(hybrid_results[:3], JD)
#         print(context[:2000])


"""
debug_hybrid.py  —  run this to confirm hybrid is now working correctly.

Usage (from app/ folder):
    python debug_hybrid.py
"""

from pinecone import Pinecone
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from ingestion.sparse import load_vectorizer, get_sparse_vector
import os

load_dotenv()

JD = "Need a backend engineer with strong experience in FastAPI, Celery, Redis, Kafka, Terraform, Kubernetes, PostgreSQL and Docker."

pc = Pinecone(api_key=os.getenv("PINECONE_AI_RESUME_ANALYST_KEY"), ssl_verify=False)
index = pc.Index("hybrid-resume-index")
model = SentenceTransformer("./768_d_model")
vectorizer = load_vectorizer()


def scale_vectors(dense_vector, sparse_vector, alpha):
    scaled_dense = [v * alpha for v in dense_vector]
    sparse_values = sparse_vector["values"]
    if sparse_values:
        magnitude = sum(v * v for v in sparse_values) ** 0.5
        if magnitude > 0:
            normalized = [v / magnitude * (1 - alpha) for v in sparse_values]
        else:
            normalized = sparse_values
    else:
        normalized = []
    return scaled_dense, {"indices": sparse_vector["indices"], "values": normalized}


dense_vector = model.encode(JD, normalize_embeddings=True).tolist()
sparse_vector = get_sparse_vector(JD, vectorizer)

print(f"\nSparse non-zero terms in JD: {len(sparse_vector['indices'])}")
print(f"Sample sparse values (raw): {[round(v,4) for v in sparse_vector['values'][:5]]}")

print("\n" + "=" * 60)
print("SCORES ACROSS ALPHA VALUES — these MUST differ now")
print("=" * 60)

for alpha in [1.0, 0.7, 0.5, 0.3, 0.0]:
    sd, ss = scale_vectors(dense_vector, sparse_vector, alpha)
    resp = index.query(
        vector=sd,
        sparse_vector=ss,
        top_k=3,
        include_metadata=True,
        include_values=False
    )
    scores = [(m.metadata.get("filename", "?"), round(m.score, 5)) for m in resp.matches]
    print(f"alpha={alpha}: {scores}")

print("\nIf scores differ across alpha values — hybrid search is WORKING correctly.")
print("If scores are still identical — paste this output and we dig deeper.")