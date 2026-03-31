from pinecone import Pinecone
from dotenv import load_dotenv
import os 
from config import PINECONE_INDEX_NAME, RESUME_DIR
from ingestion.dense import dense_embed
from ingestion.sparse import fit_and_save_vectorizer, get_sparse_vector

load_dotenv()

def upsert_to_index(path):
    """
    Full hybrid ingestion pipeline:
    1. Parse all resumes and get dense embeddings of 768-dim dense vectors (same as before)
    2. fit TF-IDF Collect all chunk texts → fit TF-IDF vectorizer → save it
    3. Sparse embeded : Attach sparse vectors to each record
    4. Upsert: push all hybrid records to Pinecone
    """
    # Step 1: Get dense records
    records = dense_embed(path)
    if not records:
        print("No records to upsert - check your resumes folder path")
        return []
    
    # Step 2: fit TF-IDF on all chunk texts we already have from dense step
    # No need to re-parse PDFs — the text is already in record["metadata"]["text"]
    all_texts = [record["metadata"]["text"] for record in records]
    vectorizer = fit_and_save_vectorizer(all_texts)

    # Step 3: Attach sparse_values to each record
    for record in records:
        chunk_text = record["metadata"]["text"]
        record["sparse_values"] = get_sparse_vector(chunk_text, vectorizer)
    
    # Step 4: upsert to pinecone
    pc = Pinecone(api_key= os.getenv("PINECONE_AI_RESUME_ANALYST_KEY"), ssl_verify= False)
    index = pc.Index(PINECONE_INDEX_NAME)

    if not index:
        print("Index not available - check your Pinecone key and index name")
        return records
    
    index.upsert(vectors= records)
    print(f"Successfully upserted {len(records)} hybrid records to '{PINECONE_INDEX_NAME}")
    return records


if __name__ == "__main__":
    folder_path = RESUME_DIR
    records = upsert_to_index(folder_path)
    if records:
        print(f"\nSample of first record upserted:")
        print(f"  id              : {records[0]['id']}")
        print(f"  dense dims      : {len(records[0]['values'])}")
        print(f"  sparse non-zeros: {len(records[0]['sparse_values']['indices'])}")